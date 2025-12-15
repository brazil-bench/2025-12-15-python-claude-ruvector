"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: brazilian_soccer_mcp
Description: Brazilian Soccer MCP Server - Knowledge graph interface for
             Brazilian soccer data using RuVector vector database
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    This package provides an MCP (Model Context Protocol) server that enables
    natural language queries about Brazilian soccer data including:
    - Match results from Brasileirao, Copa do Brasil, and Libertadores
    - Player data from FIFA database
    - Team statistics and head-to-head comparisons
    - Historical analysis and standings calculations

Components:
    - server.py: MCP server entry point and tool definitions
    - data_loader.py: CSV data loading and preprocessing
    - vector_store.py: RuVector integration for similarity search
    - query_handlers.py: Query processing and response formatting
    - models.py: Pydantic data models
    - utils.py: Utility functions (team name normalization, date parsing)

Data Sources:
    - Brasileirao_Matches.csv: 4,180 Serie A matches
    - Brazilian_Cup_Matches.csv: 1,337 Copa do Brasil matches
    - Libertadores_Matches.csv: 1,255 Libertadores matches
    - BR-Football-Dataset.csv: 10,296 extended match statistics
    - novo_campeonato_brasileiro.csv: 6,886 historical matches (2003-2019)
    - fifa_data.csv: 18,207 FIFA player records
=============================================================================
"""

__version__ = "1.0.0"
__author__ = "Hive Mind Collective"

from .models import Match, Team, Player, Competition, TeamStats
from .data_loader import DataLoader
from .vector_store import VectorStore
from .query_handlers import QueryHandler

__all__ = [
    "Match",
    "Team",
    "Player",
    "Competition",
    "TeamStats",
    "DataLoader",
    "VectorStore",
    "QueryHandler",
]
