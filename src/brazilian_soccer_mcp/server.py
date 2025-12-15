"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: server.py
Description: MCP Server entry point for Brazilian Soccer MCP Server
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Implement the MCP (Model Context Protocol) server that exposes tools
    for querying Brazilian soccer data. This server can be connected to
    LLMs like Claude to enable natural language queries about:
    - Match results and history
    - Team statistics and comparisons
    - Player information and ratings
    - Competition standings and analysis

MCP Tools Exposed:
    1. search_matches: Find matches by team, date, competition, season
    2. get_team_stats: Get team statistics (wins, losses, goals)
    3. search_players: Find players by name, nationality, club, position
    4. get_head_to_head: Compare two teams head-to-head
    5. get_standings: Calculate league standings for a season
    6. get_statistics: Various statistical analyses

Protocol:
    Uses the MCP protocol for tool exposure:
    - Tools are defined with JSON schemas
    - Requests come via stdin (JSON-RPC)
    - Responses sent via stdout (JSON-RPC)

Usage:
    Run as MCP server:
        python -m brazilian_soccer_mcp.server

    Or via entry point:
        brazilian-soccer-mcp
=============================================================================
"""

import asyncio
import json
import logging
from typing import Any, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

from .data_loader import DataLoader
from .query_handlers import QueryHandler
from .vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrazilianSoccerMCPServer:
    """
    MCP Server for Brazilian Soccer data queries.

    Provides tools for querying match data, player information,
    team statistics, and competition standings.
    """

    def __init__(self):
        """Initialize the MCP server with data loader and query handler."""
        self.data_loader = DataLoader()
        self.vector_store = VectorStore()
        self.query_handler: Optional[QueryHandler] = None
        self._initialized = False

    def initialize(self) -> None:
        """Load data and initialize query handler."""
        if self._initialized:
            return

        logger.info("Loading Brazilian soccer data...")
        self.data_loader.load_all()

        logger.info(f"Loaded {self.data_loader.total_matches} matches")
        logger.info(f"Loaded {self.data_loader.total_players} players")
        logger.info(f"Loaded {self.data_loader.total_teams} teams")

        # Index data in vector store
        logger.info("Indexing data in vector store...")
        self.vector_store.index_matches(self.data_loader.matches[:5000])  # Limit for memory
        self.vector_store.index_players(self.data_loader.players)
        logger.info(f"Indexed {self.vector_store.size} items in vector store")

        # Initialize query handler
        self.query_handler = QueryHandler(self.data_loader, self.vector_store)
        self._initialized = True
        logger.info("Server initialized successfully")

    def get_tools(self) -> list:
        """Return list of available MCP tools."""
        return [
            {
                "name": "search_matches",
                "description": "Search for Brazilian soccer matches by team, opponent, competition, season, or date range",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team": {
                            "type": "string",
                            "description": "Team name to search for (e.g., 'Flamengo', 'Palmeiras')"
                        },
                        "opponent": {
                            "type": "string",
                            "description": "Opponent team name (use with 'team' to find specific matchups)"
                        },
                        "competition": {
                            "type": "string",
                            "enum": ["brasileirao", "copa_do_brasil", "libertadores"],
                            "description": "Filter by competition"
                        },
                        "season": {
                            "type": "integer",
                            "description": "Filter by season year (e.g., 2023)"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date filter (YYYY-MM-DD format)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date filter (YYYY-MM-DD format)"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "description": "Maximum number of results to return"
                        }
                    }
                }
            },
            {
                "name": "get_team_stats",
                "description": "Get statistics for a Brazilian soccer team including wins, losses, draws, goals, and records",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team": {
                            "type": "string",
                            "description": "Team name (e.g., 'Corinthians', 'Santos')"
                        },
                        "season": {
                            "type": "integer",
                            "description": "Filter by season year"
                        },
                        "competition": {
                            "type": "string",
                            "enum": ["brasileirao", "copa_do_brasil", "libertadores"],
                            "description": "Filter by competition"
                        }
                    },
                    "required": ["team"]
                }
            },
            {
                "name": "search_players",
                "description": "Search for players in the FIFA database by name, nationality, club, or position",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Player name (partial match supported)"
                        },
                        "nationality": {
                            "type": "string",
                            "description": "Filter by nationality (e.g., 'Brazil', 'Argentina')"
                        },
                        "club": {
                            "type": "string",
                            "description": "Filter by club name (partial match supported)"
                        },
                        "position": {
                            "type": "string",
                            "description": "Filter by position (e.g., 'GK', 'CB', 'CM', 'ST')"
                        },
                        "min_overall": {
                            "type": "integer",
                            "description": "Minimum FIFA overall rating (0-99)"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 20,
                            "description": "Maximum number of results"
                        }
                    }
                }
            },
            {
                "name": "get_head_to_head",
                "description": "Get head-to-head statistics between two teams",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team1": {
                            "type": "string",
                            "description": "First team name"
                        },
                        "team2": {
                            "type": "string",
                            "description": "Second team name"
                        },
                        "competition": {
                            "type": "string",
                            "enum": ["brasileirao", "copa_do_brasil", "libertadores"],
                            "description": "Filter by competition"
                        }
                    },
                    "required": ["team1", "team2"]
                }
            },
            {
                "name": "get_standings",
                "description": "Calculate league standings for a specific season",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "season": {
                            "type": "integer",
                            "description": "Season year (e.g., 2019)"
                        },
                        "competition": {
                            "type": "string",
                            "enum": ["brasileirao", "copa_do_brasil", "libertadores"],
                            "default": "brasileirao",
                            "description": "Competition (default: brasileirao)"
                        }
                    },
                    "required": ["season"]
                }
            },
            {
                "name": "get_statistics",
                "description": "Get various statistical analyses of Brazilian soccer data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "stat_type": {
                            "type": "string",
                            "enum": ["biggest_wins", "highest_scoring", "avg_goals"],
                            "description": "Type of statistic to retrieve"
                        },
                        "season": {
                            "type": "integer",
                            "description": "Filter by season year"
                        },
                        "competition": {
                            "type": "string",
                            "enum": ["brasileirao", "copa_do_brasil", "libertadores"],
                            "description": "Filter by competition"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "description": "Maximum number of results"
                        }
                    },
                    "required": ["stat_type"]
                }
            }
        ]

    def handle_tool_call(self, name: str, arguments: dict) -> dict:
        """
        Handle a tool call and return the result.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result dictionary
        """
        if not self._initialized:
            self.initialize()

        try:
            if name == "search_matches":
                result = self.query_handler.search_matches(
                    team=arguments.get("team"),
                    opponent=arguments.get("opponent"),
                    competition=arguments.get("competition"),
                    season=arguments.get("season"),
                    start_date=arguments.get("start_date"),
                    end_date=arguments.get("end_date"),
                    limit=arguments.get("limit", 20),
                )

            elif name == "get_team_stats":
                result = self.query_handler.get_team_stats(
                    team=arguments["team"],
                    season=arguments.get("season"),
                    competition=arguments.get("competition"),
                )

            elif name == "search_players":
                result = self.query_handler.search_players(
                    name=arguments.get("name"),
                    nationality=arguments.get("nationality"),
                    club=arguments.get("club"),
                    position=arguments.get("position"),
                    min_overall=arguments.get("min_overall"),
                    limit=arguments.get("limit", 20),
                )

            elif name == "get_head_to_head":
                result = self.query_handler.get_head_to_head(
                    team1=arguments["team1"],
                    team2=arguments["team2"],
                    competition=arguments.get("competition"),
                )

            elif name == "get_standings":
                result = self.query_handler.get_standings(
                    season=arguments["season"],
                    competition=arguments.get("competition", "brasileirao"),
                )

            elif name == "get_statistics":
                result = self.query_handler.get_statistics(
                    stat_type=arguments["stat_type"],
                    season=arguments.get("season"),
                    competition=arguments.get("competition"),
                    limit=arguments.get("limit", 10),
                )

            else:
                return {"error": f"Unknown tool: {name}"}

            return result.to_response()

        except Exception as e:
            logger.error(f"Error handling tool call {name}: {e}")
            return {"error": str(e), "success": False}


# Global server instance
_server_instance: Optional[BrazilianSoccerMCPServer] = None


def get_server() -> BrazilianSoccerMCPServer:
    """Get or create the server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = BrazilianSoccerMCPServer()
    return _server_instance


async def run_mcp_server():
    """Run the MCP server using stdio transport."""
    if not HAS_MCP:
        logger.error("MCP library not installed. Install with: pip install mcp")
        return

    server = Server("brazilian-soccer-mcp")
    soccer_server = get_server()

    @server.list_tools()
    async def list_tools():
        """List available tools."""
        tools = soccer_server.get_tools()
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            )
            for t in tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls."""
        result = soccer_server.handle_tool_call(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


def main():
    """Main entry point."""
    logger.info("Starting Brazilian Soccer MCP Server...")

    if HAS_MCP:
        asyncio.run(run_mcp_server())
    else:
        # Fallback: simple CLI mode for testing
        print("MCP library not available. Running in CLI test mode.")
        server = get_server()
        server.initialize()

        # Test queries
        print("\n=== Testing Queries ===\n")

        # Test match search
        result = server.handle_tool_call("search_matches", {"team": "Flamengo", "limit": 5})
        print("Match Search (Flamengo):")
        print(json.dumps(result, indent=2, default=str)[:500] + "...")

        # Test team stats
        result = server.handle_tool_call("get_team_stats", {"team": "Palmeiras", "season": 2019})
        print("\nTeam Stats (Palmeiras 2019):")
        print(json.dumps(result, indent=2, default=str))

        # Test player search
        result = server.handle_tool_call("search_players", {"nationality": "Brazil", "min_overall": 85, "limit": 5})
        print("\nTop Brazilian Players:")
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
