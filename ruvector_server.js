/**
 * =============================================================================
 * CONTEXT BLOCK
 * =============================================================================
 * Module: ruvector_server.js
 * Description: Node.js HTTP server wrapper for RuVector vector database
 * Author: Hive Mind Collective (Queen + Workers)
 * Created: 2025-12-15
 * Updated: 2025-12-15
 *
 * Purpose:
 *   Expose RuVector's vector database capabilities via HTTP API so that
 *   Python code can use it for Brazilian Soccer MCP Server.
 *
 * Persistence:
 *   Data is automatically persisted to disk and loaded on server start.
 *   - Data directory: ./ruvector_data/ (configurable via RUVECTOR_DATA_DIR)
 *   - Auto-save: After each insert/batch operation
 *   - Auto-load: On server startup if data exists
 *
 * Endpoints:
 *   POST /init          - Initialize the vector database
 *   POST /insert        - Insert a vector with ID and metadata
 *   POST /insert_batch  - Insert multiple vectors
 *   POST /search        - Search for similar vectors
 *   POST /clear         - Clear all vectors
 *   POST /save          - Manually save to disk
 *   POST /load          - Manually load from disk
 *   GET  /stats         - Get database statistics
 *   GET  /health        - Health check
 *
 * Usage:
 *   node ruvector_server.js [port]
 *   Default port: 3456
 *
 * Environment Variables:
 *   RUVECTOR_PORT     - Server port (default: 3456)
 *   RUVECTOR_DATA_DIR - Data directory (default: ./ruvector_data)
 *   RUVECTOR_AUTO_SAVE - Auto-save after inserts (default: true)
 * =============================================================================
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const ruvector = require('ruvector');

// Configuration
const PORT = process.argv[2] || process.env.RUVECTOR_PORT || 3456;
const DATA_DIR = process.env.RUVECTOR_DATA_DIR || path.join(__dirname, 'ruvector_data');
const AUTO_SAVE = process.env.RUVECTOR_AUTO_SAVE !== 'false';
const VECTORS_FILE = path.join(DATA_DIR, 'vectors.json');
const METADATA_FILE = path.join(DATA_DIR, 'metadata.json');
const CONFIG_FILE = path.join(DATA_DIR, 'config.json');
// RuVector's internal database file (created by the Rust library)
const RUVECTOR_DB_FILE = path.join(__dirname, 'ruvector.db');

// Default embedding dimension
const DEFAULT_DIMENSION = 384;

// Global vector database instance
let vectorDb = null;
let metadata = new Map();
let currentDimension = DEFAULT_DIMENSION;
let isDirty = false; // Track if data needs saving

/**
 * Ensure data directory exists
 */
function ensureDataDir() {
    if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
        console.log(`[RuVector] Created data directory: ${DATA_DIR}`);
    }
}

/**
 * Save data to disk
 */
function saveData() {
    if (!isDirty && fs.existsSync(VECTORS_FILE)) {
        return { success: true, message: 'No changes to save' };
    }

    try {
        ensureDataDir();

        // Save config
        const config = {
            dimension: currentDimension,
            count: metadata.size,
            savedAt: new Date().toISOString()
        };
        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));

        // Save metadata
        const metadataArray = Array.from(metadata.entries());
        fs.writeFileSync(METADATA_FILE, JSON.stringify(metadataArray, null, 2));

        // Save vectors - we need to extract them from the entries
        // Since RuVector doesn't expose a way to get all vectors, we store them separately
        const vectorsData = [];
        for (const [id, meta] of metadata.entries()) {
            if (meta._vector) {
                vectorsData.push({
                    id: id,
                    vector: meta._vector
                });
            }
        }
        fs.writeFileSync(VECTORS_FILE, JSON.stringify(vectorsData, null, 2));

        isDirty = false;
        console.log(`[RuVector] Saved ${metadata.size} entries to ${DATA_DIR}`);
        return { success: true, count: metadata.size };
    } catch (error) {
        console.error('[RuVector] Save error:', error.message);
        return { success: false, error: error.message };
    }
}

/**
 * Load data from disk
 */
function loadData() {
    try {
        // Always clear RuVector's internal database on startup
        // This ensures we start with a clean state and our JSON files are the source of truth
        if (fs.existsSync(RUVECTOR_DB_FILE)) {
            fs.unlinkSync(RUVECTOR_DB_FILE);
            console.log('[RuVector] Cleared stale internal database');
        }

        if (!fs.existsSync(CONFIG_FILE)) {
            console.log('[RuVector] No saved data found');
            return { success: true, message: 'No saved data found', count: 0 };
        }

        // Load config
        const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
        const savedDimension = config.dimension || DEFAULT_DIMENSION;

        // Load vectors first to validate dimension
        let vectorsData = [];
        if (fs.existsSync(VECTORS_FILE)) {
            vectorsData = JSON.parse(fs.readFileSync(VECTORS_FILE, 'utf8'));
        }

        // Validate: check if saved vectors match config dimension
        if (vectorsData.length > 0) {
            const actualDimension = vectorsData[0].vector.length;
            if (actualDimension !== savedDimension) {
                console.log(`[RuVector] Data corruption detected: config says dimension ${savedDimension}, but vectors have dimension ${actualDimension}`);
                console.log('[RuVector] Clearing corrupted data and starting fresh');
                // Clear corrupted files
                if (fs.existsSync(VECTORS_FILE)) fs.unlinkSync(VECTORS_FILE);
                if (fs.existsSync(METADATA_FILE)) fs.unlinkSync(METADATA_FILE);
                if (fs.existsSync(CONFIG_FILE)) fs.unlinkSync(CONFIG_FILE);
                return { success: true, message: 'Cleared corrupted data', count: 0 };
            }
        }

        currentDimension = savedDimension;

        // Initialize vector database
        vectorDb = new ruvector.VectorDB({ dimensions: currentDimension });
        metadata.clear();

        // Load metadata
        if (fs.existsSync(METADATA_FILE)) {
            const metadataArray = JSON.parse(fs.readFileSync(METADATA_FILE, 'utf8'));
            for (const [id, meta] of metadataArray) {
                metadata.set(id, meta);
            }
        }

        // Load vectors into RuVector
        if (vectorsData.length > 0) {
            const entries = vectorsData.map(item => ({
                id: item.id,
                vector: ruvector.toFloat32Array(item.vector),
                metadata: JSON.stringify(metadata.get(item.id) || {})
            }));

            vectorDb.insertBatch(entries);
        }

        isDirty = false;
        console.log(`[RuVector] Loaded ${metadata.size} entries from ${DATA_DIR}`);
        return { success: true, count: metadata.size, dimension: currentDimension };
    } catch (error) {
        console.error('[RuVector] Load error:', error.message);
        return { success: false, error: error.message };
    }
}

/**
 * Initialize the vector database
 */
function initDb(dimension = DEFAULT_DIMENSION) {
    try {
        currentDimension = dimension;
        vectorDb = new ruvector.VectorDB({ dimensions: dimension });
        metadata.clear();
        isDirty = true;
        console.log(`[RuVector] Initialized VectorDB with dimension ${dimension}`);
        return { success: true, dimension };
    } catch (error) {
        console.error('[RuVector] Init error:', error.message);
        return { success: false, error: error.message };
    }
}

/**
 * Insert a single vector with metadata
 */
function insertVector(id, vector, meta = {}) {
    try {
        const newDimension = vector.length;

        // Initialize if not yet initialized
        if (!vectorDb) {
            initDb(newDimension);
        } else if (newDimension !== currentDimension) {
            // Dimension mismatch - cannot change dimensions in a running server
            // Due to RuVector's internal state management, changing dimensions requires a server restart
            const errorMsg = `Dimension mismatch: database has dimension ${currentDimension}, but received vector with dimension ${newDimension}. To change dimensions: 1) Call /clear endpoint, 2) Restart the server. This is required due to RuVector's internal state management.`;
            console.log(`[RuVector] ${errorMsg}`);
            return {
                success: false,
                error: errorMsg,
                currentDimension: currentDimension,
                requestedDimension: newDimension,
                action: 'restart_required'
            };
        }

        // Convert to Float32Array if needed
        const floatVector = ruvector.toFloat32Array(vector);

        // Insert into ruvector
        vectorDb.insert({
            id: id,
            vector: floatVector,
            metadata: JSON.stringify(meta)
        });

        // Store metadata locally (including vector for persistence)
        metadata.set(id, { ...meta, id, _vector: Array.from(vector) });
        isDirty = true;

        // Auto-save if enabled
        if (AUTO_SAVE) {
            saveData();
        }

        return { success: true, id };
    } catch (error) {
        console.error('[RuVector] Insert error:', error.message);
        return { success: false, error: error.message };
    }
}

/**
 * Insert multiple vectors in batch
 */
function insertBatch(items) {
    try {
        if (items.length === 0) {
            return { success: true, inserted: 0 };
        }

        const newDimension = items[0].vector.length;

        // Initialize if not yet initialized
        if (!vectorDb) {
            initDb(newDimension);
        } else if (newDimension !== currentDimension) {
            // Dimension mismatch - cannot change dimensions in a running server
            // Due to RuVector's internal state management, changing dimensions requires a server restart
            const errorMsg = `Dimension mismatch: database has dimension ${currentDimension}, but received vectors with dimension ${newDimension}. To change dimensions: 1) Call /clear endpoint, 2) Restart the server. This is required due to RuVector's internal state management.`;
            console.log(`[RuVector] ${errorMsg}`);
            return {
                success: false,
                error: errorMsg,
                currentDimension: currentDimension,
                requestedDimension: newDimension,
                action: 'restart_required'
            };
        }

        // Prepare entries for batch insert
        const entries = items.map(item => ({
            id: item.id,
            vector: ruvector.toFloat32Array(item.vector),
            metadata: JSON.stringify(item.metadata || {})
        }));

        // Use batch insert
        vectorDb.insertBatch(entries);

        // Store metadata locally (including vectors for persistence)
        for (const item of items) {
            metadata.set(item.id, {
                ...item.metadata,
                id: item.id,
                _vector: Array.from(item.vector)
            });
        }
        isDirty = true;

        // Auto-save if enabled
        if (AUTO_SAVE) {
            saveData();
        }

        return { success: true, inserted: items.length };
    } catch (error) {
        console.error('[RuVector] Batch insert error:', error.message);
        return { success: false, error: error.message };
    }
}

/**
 * Search for similar vectors
 */
function searchVectors(queryVector, k = 10) {
    try {
        if (!vectorDb) {
            return { success: true, results: [] };
        }

        const floatQuery = ruvector.toFloat32Array(queryVector);

        // Search in ruvector
        const searchResults = vectorDb.search({
            vector: floatQuery,
            k: k
        });

        // Add metadata to results (exclude internal _vector field)
        const results = searchResults.map(result => {
            const meta = metadata.get(result.id) || {};
            const { _vector, ...cleanMeta } = meta; // Remove _vector from response
            return {
                id: result.id,
                score: result.score,
                metadata: cleanMeta
            };
        });

        return { success: true, results };
    } catch (error) {
        console.error('[RuVector] Search error:', error.message);
        return { success: false, error: error.message, results: [] };
    }
}

/**
 * Clear all vectors
 */
function clearDb() {
    try {
        vectorDb = null;
        metadata.clear();
        isDirty = true;

        // Clear persisted data (our JSON files)
        if (fs.existsSync(VECTORS_FILE)) fs.unlinkSync(VECTORS_FILE);
        if (fs.existsSync(METADATA_FILE)) fs.unlinkSync(METADATA_FILE);
        if (fs.existsSync(CONFIG_FILE)) fs.unlinkSync(CONFIG_FILE);

        // Also clear RuVector's internal database file
        if (fs.existsSync(RUVECTOR_DB_FILE)) {
            fs.unlinkSync(RUVECTOR_DB_FILE);
            console.log('[RuVector] Deleted internal database file');
        }

        console.log('[RuVector] Cleared all data');
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

/**
 * Get database statistics
 */
function getStats() {
    const dataExists = fs.existsSync(CONFIG_FILE);
    let diskSize = 0;

    if (fs.existsSync(VECTORS_FILE)) {
        diskSize += fs.statSync(VECTORS_FILE).size;
    }
    if (fs.existsSync(METADATA_FILE)) {
        diskSize += fs.statSync(METADATA_FILE).size;
    }

    return {
        success: true,
        initialized: vectorDb !== null,
        count: metadata.size,
        dimension: currentDimension,
        dataDir: DATA_DIR,
        persistedToDisk: dataExists,
        diskSizeBytes: diskSize,
        autoSave: AUTO_SAVE,
        isDirty: isDirty
    };
}

/**
 * Parse JSON body from request
 */
function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

/**
 * HTTP request handler
 */
async function handleRequest(req, res) {
    const url = req.url;
    const method = req.method;

    // CORS headers
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    try {
        let result;

        if (url === '/health' && method === 'GET') {
            result = { status: 'ok', service: 'ruvector', persisted: fs.existsSync(CONFIG_FILE) };
        }
        else if (url === '/stats' && method === 'GET') {
            result = getStats();
        }
        else if (url === '/init' && method === 'POST') {
            const body = await parseBody(req);
            result = initDb(body.dimension || DEFAULT_DIMENSION);
        }
        else if (url === '/insert' && method === 'POST') {
            const body = await parseBody(req);
            result = insertVector(body.id, body.vector, body.metadata);
        }
        else if (url === '/insert_batch' && method === 'POST') {
            const body = await parseBody(req);
            result = insertBatch(body.items || []);
        }
        else if (url === '/search' && method === 'POST') {
            const body = await parseBody(req);
            result = searchVectors(body.vector, body.k || 10);
        }
        else if (url === '/clear' && method === 'POST') {
            result = clearDb();
        }
        else if (url === '/save' && method === 'POST') {
            result = saveData();
        }
        else if (url === '/load' && method === 'POST') {
            result = loadData();
        }
        else {
            res.writeHead(404);
            result = { error: 'Not found' };
        }

        res.writeHead(200);
        res.end(JSON.stringify(result));

    } catch (error) {
        console.error('[RuVector] Request error:', error.message);
        res.writeHead(500);
        res.end(JSON.stringify({ error: error.message }));
    }
}

// Create and start server
const server = http.createServer(handleRequest);

server.listen(PORT, () => {
    console.log(`[RuVector] Server running on http://localhost:${PORT}`);
    console.log(`[RuVector] Data directory: ${DATA_DIR}`);
    console.log(`[RuVector] Auto-save: ${AUTO_SAVE}`);
    console.log('[RuVector] Endpoints:');
    console.log('  GET  /health       - Health check');
    console.log('  GET  /stats        - Database statistics');
    console.log('  POST /init         - Initialize database');
    console.log('  POST /insert       - Insert single vector');
    console.log('  POST /insert_batch - Insert multiple vectors');
    console.log('  POST /search       - Search similar vectors');
    console.log('  POST /clear        - Clear database');
    console.log('  POST /save         - Save to disk');
    console.log('  POST /load         - Load from disk');

    // Auto-load existing data on startup
    console.log('[RuVector] Checking for existing data...');
    const loadResult = loadData();
    if (loadResult.count > 0) {
        console.log(`[RuVector] Loaded ${loadResult.count} entries from disk`);
    }
});

// Handle shutdown - save data before exit
process.on('SIGINT', () => {
    console.log('\n[RuVector] Shutting down...');
    if (isDirty) {
        console.log('[RuVector] Saving data before exit...');
        saveData();
    }
    server.close(() => process.exit(0));
});

process.on('SIGTERM', () => {
    console.log('\n[RuVector] Received SIGTERM...');
    if (isDirty) {
        console.log('[RuVector] Saving data before exit...');
        saveData();
    }
    server.close(() => process.exit(0));
});
