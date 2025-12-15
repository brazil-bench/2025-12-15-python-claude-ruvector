# Brazilian Soccer MCP Server

A Model Context Protocol (MCP) server that provides a knowledge graph interface for Brazilian soccer data, using vector similarity search for semantic queries.

## Overview

This project implements an MCP server that enables natural language queries about Brazilian soccer data including:
- Match results from Brasileirão Serie A, Copa do Brasil, and Copa Libertadores
- Player information from FIFA database (18,207 players)
- Team statistics and head-to-head comparisons
- Historical analysis and standings calculations

## Architecture

```
brazilian-soccer-mcp/
├── src/
│   └── brazilian_soccer_mcp/
│       ├── __init__.py          # Package initialization
│       ├── server.py            # MCP server entry point
│       ├── data_loader.py       # CSV data loading and preprocessing
│       ├── vector_store.py      # Vector similarity search (RuVector-style)
│       ├── query_handlers.py    # Query processing logic
│       ├── models.py            # Pydantic data models
│       └── utils.py             # Utility functions
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   └── features/                # BDD-style test modules
│       ├── test_match_queries.py
│       ├── test_team_queries.py
│       ├── test_player_queries.py
│       └── test_statistics.py
├── data/
│   └── kaggle/                  # CSV data files
└── pyproject.toml               # Project configuration
```

## Vector Store Implementation

Instead of Neo4j, this implementation uses a **RuVector-inspired vector store** approach:
- **numpy-based vector operations** for efficient similarity search
- **Sentence embeddings** for semantic search capabilities
- **Metadata filtering** combined with vector search
- **Cosine similarity** for finding related matches and players

This provides the core benefits of RuVector:
- Sub-millisecond similarity search
- Semantic query understanding
- Metadata-based filtering
- No external database dependency

## Data Sources

All datasets are included in `data/kaggle/`:

| File | Records | Description | License |
|------|---------|-------------|---------|
| Brasileirao_Matches.csv | 4,180 | Serie A matches (2012+) | CC BY 4.0 |
| Brazilian_Cup_Matches.csv | 1,337 | Copa do Brasil matches | CC BY 4.0 |
| Libertadores_Matches.csv | 1,255 | Copa Libertadores matches | CC BY 4.0 |
| BR-Football-Dataset.csv | 10,296 | Extended match statistics | CC0 |
| novo_campeonato_brasileiro.csv | 6,886 | Historical matches (2003-2019) | CC BY 4.0 |
| fifa_data.csv | 18,207 | FIFA player database | Apache 2.0 |

**Total: 23,954 matches and 18,207 players**

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/brazilian-soccer-mcp.git
cd brazilian-soccer-mcp

# Install dependencies
pip install -e ".[dev]"
```

## Usage

### As MCP Server

```bash
# Run the MCP server
python -m brazilian_soccer_mcp.server
```

### As Python Library

```python
from brazilian_soccer_mcp import DataLoader, QueryHandler

# Load data
loader = DataLoader()
loader.load_all()

# Create query handler
handler = QueryHandler(loader)

# Search matches
result = handler.search_matches(team="Flamengo", opponent="Fluminense")
print(result.message)

# Get team statistics
stats = handler.get_team_stats(team="Palmeiras", season=2023)
print(stats.data)

# Search players
players = handler.search_players(nationality="Brazil", min_overall=85)
print(f"Found {players.count} players")

# Get head-to-head
h2h = handler.get_head_to_head(team1="Corinthians", team2="Palmeiras")
print(h2h.message)
```

## MCP Tools

The server exposes the following tools:

| Tool | Description |
|------|-------------|
| `search_matches` | Find matches by team, opponent, competition, season, date range |
| `get_team_stats` | Get team statistics (wins, losses, goals, records) |
| `search_players` | Find players by name, nationality, club, position, rating |
| `get_head_to_head` | Compare two teams head-to-head |
| `get_standings` | Calculate league standings for a season |
| `get_statistics` | Various statistical analyses (biggest wins, averages) |

## Query Examples

### Match Queries
```python
# Find Fla-Flu derby matches
handler.search_matches(team="Flamengo", opponent="Fluminense")

# Find all 2019 Brasileirão matches
handler.search_matches(competition="brasileirao", season=2019)

# Find Copa Libertadores matches
handler.search_matches(competition="libertadores", limit=50)
```

### Team Queries
```python
# Get Flamengo's 2019 championship stats
handler.get_team_stats(team="Flamengo", season=2019)

# Get head-to-head: Gre-Nal derby
handler.get_head_to_head(team1="Gremio", team2="Internacional")
```

### Player Queries
```python
# Find Brazilian players rated 85+
handler.search_players(nationality="Brazil", min_overall=85)

# Find Flamengo players
handler.search_players(club="Flamengo")

# Find strikers
handler.search_players(position="ST", limit=20)
```

### Statistics
```python
# Calculate 2019 standings
handler.get_standings(season=2019)

# Find biggest wins
handler.get_statistics(stat_type="biggest_wins", limit=10)

# Calculate average goals per match
handler.get_statistics(stat_type="avg_goals")
```

## Testing

The project uses BDD (Behavior-Driven Development) style tests with Given-When-Then format:

```bash
# Run all tests
pytest tests/features/ -v

# Run specific test category
pytest tests/features/test_match_queries.py -v
pytest tests/features/test_team_queries.py -v
pytest tests/features/test_player_queries.py -v
pytest tests/features/test_statistics.py -v

# Run with coverage
pytest tests/features/ --cov=brazilian_soccer_mcp --cov-report=html
```

### Test Results

```
47 tests passed in 8.73s
- test_match_queries.py: 13 tests
- test_team_queries.py: 10 tests
- test_player_queries.py: 12 tests
- test_statistics.py: 12 tests
```

## Project Features

### Data Handling
- **Team name normalization**: Handles variations like "Palmeiras-SP" vs "Palmeiras"
- **Multiple date formats**: Supports ISO, Brazilian, and datetime formats
- **UTF-8 encoding**: Proper handling of Portuguese characters (São, Grêmio, Avaí)
- **Classic derby detection**: Identifies Fla-Flu, Gre-Nal, Derby Paulista, etc.

### Query Capabilities
- **Match search** with multiple filters (team, opponent, competition, season, date range)
- **Team statistics** including home/away breakdown
- **Player search** with nationality, club, position, and rating filters
- **Head-to-head** comparisons with historical data
- **League standings** calculated from match results
- **Statistical analysis** (biggest wins, goal averages, etc.)

### Vector Search
- **Semantic search** for natural language queries
- **Similarity-based** player and match recommendations
- **Hybrid search** combining keyword and vector matching

## License

MIT License

## Data Attribution

- Brazilian Soccer Matches: [Kaggle - Ricardo Mattos](https://www.kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro) - CC BY 4.0
- Brazilian Football Matches: [Kaggle - Cuecacuela](https://www.kaggle.com/datasets/cuecacuela/brazilian-football-matches) - CC0
- Campeonato Brasileiro 2003-2019: [Kaggle - macedojleo](https://www.kaggle.com/datasets/macedojleo/campeonato-brasileiro-2003-a-2019) - CC BY 4.0
- FIFA Players Data: [Kaggle - Youssef Elbadry](https://www.kaggle.com/datasets/youssefelbadry10/fifa-players-data) - Apache 2.0

## RuVector Integration Details

The project integrates with [RuVector](https://github.com/ruvnet/ruvector) via a Node.js HTTP bridge:

### Architecture
```
Python (vector_store.py) <--HTTP--> Node.js (ruvector_server.js) <--N-API--> RuVector (Rust)
```

### RuVector Server Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/stats` | GET | Database statistics |
| `/init` | POST | Initialize with dimension |
| `/insert` | POST | Insert single vector |
| `/insert_batch` | POST | Insert multiple vectors |
| `/search` | POST | Search similar vectors |
| `/clear` | POST | Clear all vectors |

### Starting the RuVector Server (Required)
```bash
# Install RuVector
npm install ruvector

# Start server (default port 3456)
node ruvector_server.js

# Or specify port
node ruvector_server.js 8080
```

**Note:** The RuVector server must be running for vector operations. The system will raise a `RuVectorConnectionError` if the server is unavailable.

## Test Results

All 47 BDD tests pass:

```
tests/features/test_match_queries.py    - 13 tests ✓
tests/features/test_player_queries.py   - 12 tests ✓
tests/features/test_team_queries.py     - 10 tests ✓
tests/features/test_statistics.py       - 12 tests ✓

============================== 47 passed in 8.61s ==============================
```

### Test Categories
- **Match Queries**: Find matches by team, competition, season, date range
- **Player Queries**: Search by name, nationality, club, position, rating
- **Team Queries**: Statistics, head-to-head comparisons, home/away records
- **Statistics**: Standings calculation, biggest wins, goal averages

## Implementation Notes

This project was implemented using a **Hive Mind Collective** approach with specialized agents:
- **Researcher Agent**: Analyzed RuVector documentation and API patterns
- **Analyst Agent**: Designed the MCP server architecture
- **Coder Agent**: Implemented core functionality
- **Tester Agent**: Created comprehensive BDD test suite

The implementation uses RuVector exclusively for vector storage and similarity search. The RuVector server must be running for vector operations to work.

## Context Block Documentation

All source files include a detailed context block comment at the top describing:
- Module purpose and functionality
- Author and creation date
- Architecture decisions
- Key functions/classes
- Dependencies and relationships

Example:
```python
"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: vector_store.py
Description: Vector store implementation using RuVector for Brazilian Soccer MCP
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15
...
=============================================================================
"""
```

## Success Criteria Met

### Functional Requirements ✓
- [x] Can search and return match data from all provided CSV files
- [x] Can search and return player data
- [x] Can calculate basic statistics (wins, losses, goals)
- [x] Can compare teams head-to-head
- [x] Handles team name variations correctly
- [x] Returns properly formatted responses

### Data Coverage ✓
- [x] All 6 CSV files are loadable and queryable
- [x] 47 test scenarios pass (exceeds 20 sample questions requirement)
- [x] Cross-file queries work (player + match data)

### Technical Implementation ✓
- [x] Uses RuVector instead of Neo4j as specified
- [x] BDD-style tests with Given-When-Then format
- [x] Context block comments in all code files
- [x] Comprehensive README documentation
