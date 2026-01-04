"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_player_queries.py
Description: pytest-bdd step definitions for player query tests
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15
Updated: 2026-01-04

Purpose:
    BDD step definitions for player search functionality using pytest-bdd
    with Gherkin .feature files.
=============================================================================
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the feature file
scenarios('gherkin/player_queries.feature')


# Shared context storage
@pytest.fixture
def context():
    """Shared context for passing data between steps."""
    return {}


# Background step
@given("the player data is loaded")
def player_data_loaded(query_handler):
    """Verify that player data is available."""
    assert query_handler is not None, "Query handler should be initialized"


# When steps for player searches
@when(parsers.parse('I search for player "{name}"'))
def search_player_by_name(query_handler, context, name):
    """Search for a player by name."""
    result = query_handler.search_players(name=name)
    context['result'] = result


@when(parsers.parse('I filter players by nationality "{nationality}"'))
def filter_players_by_nationality(query_handler, context, nationality):
    """Filter players by nationality."""
    result = query_handler.search_players(nationality=nationality, limit=50)
    context['result'] = result


@when(parsers.parse('I filter players by club "{club}"'))
def filter_players_by_club(query_handler, context, club):
    """Filter players by club."""
    result = query_handler.search_players(club=club, limit=30)
    context['result'] = result


@when(parsers.parse('I filter players by position "{position}"'))
def filter_players_by_position(query_handler, context, position):
    """Filter players by position."""
    result = query_handler.search_players(position=position, limit=30)
    context['result'] = result


@when(parsers.parse('I search for "{nationality}" players with minimum rating {rating:d}'))
def search_players_by_nationality_and_rating(query_handler, context, nationality, rating):
    """Search for players by nationality with minimum rating."""
    result = query_handler.search_players(nationality=nationality, min_overall=rating, limit=20)
    context['result'] = result


@when(parsers.parse('I search for players with minimum rating {rating:d}'))
def search_players_by_rating(query_handler, context, rating):
    """Search for players with minimum rating."""
    result = query_handler.search_players(min_overall=rating, limit=10)
    context['result'] = result


# Then steps
@then("the query should succeed")
def query_should_succeed(context):
    """Verify the query succeeded."""
    result = context['result']
    assert result.success, "Query should succeed"


@then("I should find players")
def should_find_players(context):
    """Verify that players were found."""
    result = context['result']
    assert result.success, "Query should succeed"
    assert result.count > 0, "Should find players"


@then(parsers.parse('the results should include "{name}"'))
def results_include_name(context, name):
    """Verify the results include a specific player name."""
    result = context['result']
    if result.data:
        names = [p["name"] for p in result.data]
        assert any(name in n for n in names), f"Should include {name}"


@then(parsers.parse('all players should be from "{nationality}"'))
def all_players_from_nationality(context, nationality):
    """Verify all players are from the specified nationality."""
    result = context['result']
    for player in result.data[:10]:
        assert player.get("nationality") == nationality, \
            f"Player should be from {nationality}"


@then("players should be sorted by rating descending")
def players_sorted_by_rating(context):
    """Verify players are sorted by rating descending."""
    result = context['result']
    if result.data and len(result.data) > 1:
        ratings = [p.get("overall", 0) for p in result.data]
        assert ratings == sorted(ratings, reverse=True), \
            "Players should be sorted by rating"


@then("all players should have rating 90 or above")
def all_players_high_rating(context):
    """Verify all players have rating 90 or above."""
    result = context['result']
    for player in result.data:
        assert player.get("overall", 0) >= 90, "Player should have 90+ rating"


@then("the result should be empty")
def result_should_be_empty(context):
    """Verify the result is empty."""
    result = context['result']
    assert result.count == 0, "Should return empty results"
