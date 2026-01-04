"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: conftest.py
Description: Shared pytest fixtures for Brazilian Soccer MCP Server tests
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15
Updated: 2026-01-04

Purpose:
    Provide shared test fixtures for all test modules including:
    - Data loader with test data
    - Query handler for running queries
    - Vector store for semantic search tests (requires RuVector server)
    - Sample data for specific test scenarios

    Tests use pytest-bdd with Gherkin .feature files for BDD-style testing.
    Feature files are located in tests/features/gherkin/

Fixtures:
    - data_loader: Loaded DataLoader instance with all CSV data
    - query_handler: QueryHandler instance for query tests
    - vector_store: VectorStore instance (requires RuVector server running)
    - sample_matches: Sample match data for unit tests
    - sample_players: Sample player data for unit tests

Note:
    Vector store tests require the RuVector server to be running.
    Start with: node ruvector_server.js
=============================================================================
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from brazilian_soccer_mcp.data_loader import DataLoader
from brazilian_soccer_mcp.query_handlers import QueryHandler
from brazilian_soccer_mcp.vector_store import VectorStore, RuVectorConnectionError
from brazilian_soccer_mcp.models import Match, Player, Competition
from datetime import datetime


@pytest.fixture(scope="session")
def data_dir():
    """Return path to data directory."""
    return Path(__file__).parent.parent / "data" / "kaggle"


@pytest.fixture(scope="session")
def data_loader(data_dir):
    """
    Load all data from CSV files.

    This fixture is session-scoped to avoid reloading data for every test.
    """
    loader = DataLoader(str(data_dir))
    loader.load_all()
    return loader


@pytest.fixture(scope="session")
def query_handler(data_loader):
    """
    Create a QueryHandler instance with loaded data.
    """
    return QueryHandler(data_loader)


@pytest.fixture(scope="session")
def vector_store(data_loader):
    """
    Create and populate a VectorStore instance.

    Requires RuVector server to be running.
    Skips tests if server is unavailable.
    """
    try:
        store = VectorStore()
        # Index a subset of matches for faster tests
        store.index_matches(data_loader.matches[:1000])
        store.index_players(data_loader.players[:500])
        return store
    except RuVectorConnectionError:
        pytest.skip("RuVector server not available. Start with: node ruvector_server.js")


@pytest.fixture(scope="session")
def query_handler_with_vector_store(data_loader, vector_store):
    """
    Create a QueryHandler with vector store enabled.

    Requires RuVector server to be running.
    """
    return QueryHandler(data_loader, vector_store)


@pytest.fixture
def sample_matches():
    """
    Create sample match data for unit tests.
    """
    return [
        Match(
            match_date=datetime(2023, 5, 15),
            home_team="Flamengo",
            away_team="Fluminense",
            home_goals=2,
            away_goals=1,
            season=2023,
            match_round=10,
            competition=Competition.BRASILEIRAO,
        ),
        Match(
            match_date=datetime(2023, 8, 20),
            home_team="Fluminense",
            away_team="Flamengo",
            home_goals=1,
            away_goals=1,
            season=2023,
            match_round=20,
            competition=Competition.BRASILEIRAO,
        ),
        Match(
            match_date=datetime(2023, 3, 10),
            home_team="Palmeiras",
            away_team="Corinthians",
            home_goals=3,
            away_goals=0,
            season=2023,
            match_round=5,
            competition=Competition.BRASILEIRAO,
        ),
        Match(
            match_date=datetime(2022, 11, 15),
            home_team="Flamengo",
            away_team="Palmeiras",
            home_goals=0,
            away_goals=2,
            season=2022,
            match_round=38,
            competition=Competition.BRASILEIRAO,
        ),
    ]


@pytest.fixture
def sample_players():
    """
    Create sample player data for unit tests.
    """
    return [
        Player(
            id=1,
            name="Gabriel Barbosa",
            age=27,
            nationality="Brazil",
            overall=83,
            potential=85,
            club="Flamengo",
            position="ST",
        ),
        Player(
            id=2,
            name="Raphael Veiga",
            age=28,
            nationality="Brazil",
            overall=82,
            potential=82,
            club="Palmeiras",
            position="CAM",
        ),
        Player(
            id=3,
            name="Neymar Jr",
            age=31,
            nationality="Brazil",
            overall=89,
            potential=89,
            club="Al-Hilal",
            position="LW",
        ),
        Player(
            id=4,
            name="Lionel Messi",
            age=36,
            nationality="Argentina",
            overall=90,
            potential=90,
            club="Inter Miami",
            position="RW",
        ),
    ]


