/**
 * =============================================================================
 * CONTEXT BLOCK
 * =============================================================================
 * Module: ruvector_server.js
 * Description: Node.js HTTP server wrapper for RuVector vector database
 * Author: Hive Mind Collective (Queen + Workers)
 * Created: 2025-12-15
 *
 * Purpose:
 *   Expose RuVector's vector database capabilities via HTTP API so that
 *   Python code can use it for Brazilian Soccer MCP Server.
 *
 * Endpoints:
 *   POST /init          - Initialize the vector database
 *   POST /insert        - Insert a vector with ID and metadata
 *   POST /insert_batch  - Insert multiple vectors
 *   POST /search        - Search for similar vectors
 *   POST /clear         - Clear all vectors
 *   GET  /stats         - Get database statistics
 *   GET  /health        - Health check
 *
 * Usage:
 *   node ruvector_server.js [port]
 *   Default port: 3456
 * =============================================================================
 */

const http = require('http');
const ruvector = require('ruvector');

// Configuration
const PORT = process.argv[2] || 3456;
const DIMENSION = 384; // Default embedding dimension

// Global vector database instance
let vectorDb = null;
let metadata = new Map(); // Store metadata separately

/**
 * Initialize the vector database
 */
function initDb(dimension = DIMENSION) {
    try {
        // RuVector expects an options object with 'dimensions' (plural)
        vectorDb = new ruvector.VectorDB({ dimensions: dimension });
        metadata.clear();
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
        if (!vectorDb) {
            initDb(vector.length);
        }

        // Convert to Float32Array if needed
        const floatVector = ruvector.toFloat32Array(vector);

        // Insert into ruvector using the entry format
        vectorDb.insert({
            id: id,
            vector: floatVector,
            metadata: JSON.stringify(meta)
        });

        // Store metadata locally for retrieval
        metadata.set(id, { ...meta, id });

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
        if (!vectorDb && items.length > 0) {
            initDb(items[0].vector.length);
        }

        // Prepare entries for batch insert
        const entries = items.map(item => ({
            id: item.id,
            vector: ruvector.toFloat32Array(item.vector),
            metadata: JSON.stringify(item.metadata || {})
        }));

        // Use batch insert
        vectorDb.insertBatch(entries);

        // Store metadata locally
        for (const item of items) {
            metadata.set(item.id, { ...item.metadata, id: item.id });
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
function searchVectors(queryVector, k = 10, filterFn = null) {
    try {
        if (!vectorDb) {
            return { success: true, results: [] };
        }

        const floatQuery = ruvector.toFloat32Array(queryVector);

        // Search in ruvector using query object format
        const searchResults = vectorDb.search({
            vector: floatQuery,
            k: k * 2 // Get more to filter
        });

        // Apply filter and add metadata
        let filtered = [];
        for (const result of searchResults) {
            const meta = metadata.get(result.id) || {};

            // Apply filter if provided
            if (filterFn) {
                try {
                    if (!filterFn(meta)) continue;
                } catch (e) {
                    // Skip filter errors
                }
            }

            filtered.push({
                id: result.id,
                score: result.score, // RuVector returns score directly
                metadata: meta
            });

            if (filtered.length >= k) break;
        }

        return { success: true, results: filtered };
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
        return { success: true };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

/**
 * Get database statistics
 */
function getStats() {
    return {
        success: true,
        initialized: vectorDb !== null,
        count: metadata.size,
        version: ruvector.getVersion ? ruvector.getVersion() : 'unknown',
        isNative: ruvector.isNative ? ruvector.isNative() : false
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
            result = { status: 'ok', service: 'ruvector' };
        }
        else if (url === '/stats' && method === 'GET') {
            result = getStats();
        }
        else if (url === '/init' && method === 'POST') {
            const body = await parseBody(req);
            result = initDb(body.dimension || DIMENSION);
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
    console.log('[RuVector] Endpoints:');
    console.log('  GET  /health       - Health check');
    console.log('  GET  /stats        - Database statistics');
    console.log('  POST /init         - Initialize database');
    console.log('  POST /insert       - Insert single vector');
    console.log('  POST /insert_batch - Insert multiple vectors');
    console.log('  POST /search       - Search similar vectors');
    console.log('  POST /clear        - Clear database');
});

// Handle shutdown
process.on('SIGINT', () => {
    console.log('\n[RuVector] Shutting down...');
    server.close(() => process.exit(0));
});
