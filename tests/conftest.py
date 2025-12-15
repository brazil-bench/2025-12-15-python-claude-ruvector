"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: conftest.py
Description: Shared pytest fixtures for Brazilian Soccer MCP Server tests
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Provide shared test fixtures for all test modules including:
    - Data loader with test data
    - Query handler for running queries
    - Vector store for semantic search tests
    - Sample data for specific test scenarios

Fixtures:
    - data_loader: Loaded DataLoader instance with all CSV data
    - query_handler: QueryHandler instance for query tests
    - vector_store: VectorStore instance for semantic search tests
    - sample_matches: Sample match data for unit tests
    - sample_players: Sample player data for unit tests
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
from brazilian_soccer_mcp.vector_store import VectorStore
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
    """
    store = VectorStore()
    # Index a subset of matches for faster tests
    store.index_matches(data_loader.matches[:1000])
    store.index_players(data_loader.players[:500])
    return store


@pytest.fixture(scope="session")
def query_handler_with_vector_store(data_loader, vector_store):
    """
    Create a QueryHandler with vector store enabled.
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


# BDD Helper Classes
class GivenWhenThen:
    """
    Base class for BDD-style test scenarios.

    Usage:
        scenario = GivenWhenThen()
        scenario.given("the match data is loaded", data_loader is not None)
        scenario.when("I search for Flamengo matches", result := handler.search_matches(team="Flamengo"))
        scenario.then("I should get matches", len(result.data) > 0)
    """

    def __init__(self):
        self.given_conditions = []
        self.when_actions = []
        self.then_assertions = []
        self._context = {}

    def given(self, description: str, condition: bool = True):
        """Record a Given condition."""
        self.given_conditions.append((description, condition))
        assert condition, f"Given '{description}' failed"
        return self

    def when(self, description: str, action_result=None):
        """Record a When action and its result."""
        self.when_actions.append((description, action_result))
        self._context["result"] = action_result
        return self

    def then(self, description: str, assertion: bool):
        """Record and check a Then assertion."""
        self.then_assertions.append((description, assertion))
        assert assertion, f"Then '{description}' failed"
        return self

    @property
    def result(self):
        """Get the result from the When action."""
        return self._context.get("result")


@pytest.fixture
def bdd():
    """Create a new GivenWhenThen scenario helper."""
    return GivenWhenThen()
