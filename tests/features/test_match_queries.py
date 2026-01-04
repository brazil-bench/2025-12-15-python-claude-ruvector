"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_match_queries.py
Description: pytest-bdd step definitions for match query tests
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15
Updated: 2026-01-04

Purpose:
    BDD step definitions for match query functionality using pytest-bdd
    with Gherkin .feature files.
=============================================================================
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the feature file
scenarios('gherkin/match_queries.feature')


# Shared context storage
@pytest.fixture
def context():
    """Shared context for passing data between steps."""
    return {}


# Background step
@given("the match data is loaded")
def match_data_loaded(query_handler):
    """Verify that match data is available."""
    assert query_handler is not None, "Query handler should be initialized"


# When steps for finding matches between teams
@when(parsers.parse('I search for matches between "{team1}" and "{team2}"'))
def search_matches_between_teams(query_handler, context, team1, team2):
    """Search for matches between two specific teams."""
    result = query_handler.search_matches(team=team1, opponent=team2, limit=50)
    context['result'] = result


@when(parsers.parse('I filter for "{competition}" competition matches'))
def filter_by_competition(query_handler, context, competition):
    """Filter matches by competition."""
    result = query_handler.search_matches(competition=competition, limit=100)
    context['result'] = result


@when(parsers.parse('I filter for season {season:d} matches'))
def filter_by_season(query_handler, context, season):
    """Filter matches by season."""
    result = query_handler.search_matches(season=season, limit=100)
    context['result'] = result


@when(parsers.parse('I search for "{team}" matches in season {season:d}'))
def search_team_matches_in_season(query_handler, context, team, season):
    """Search for team matches in a specific season."""
    result = query_handler.search_matches(team=team, season=season, limit=50)
    context['result'] = result


@when(parsers.parse('I search for "{team}" matches'))
def search_team_matches(query_handler, context, team):
    """Search for matches of a specific team."""
    result = query_handler.search_matches(team=team, limit=20)
    context['result'] = result


@when(parsers.parse('I search for all matches with limit {limit:d}'))
def search_all_matches(query_handler, context, limit):
    """Search for all matches with a limit."""
    result = query_handler.search_matches(limit=limit)
    context['result'] = result


# Then steps
@then("I should receive matches")
def should_receive_matches(context):
    """Verify that matches were returned."""
    result = context['result']
    assert result.success, "Query should succeed"
    assert result.count > 0, "Should find matches"


@then("the query should succeed")
def query_should_succeed(context):
    """Verify that the query succeeded."""
    result = context['result']
    assert result.success, "Query should succeed"


@then("each match should have required fields")
def matches_have_required_fields(context):
    """Verify matches have all required fields."""
    result = context['result']
    for match in result.data[:5]:
        assert all(k in match for k in ["date", "home_team", "away_team", "score"]), \
            "Match should have all required fields"


@then(parsers.parse('all matches should be from "{competition}" competition'))
def matches_from_competition(context, competition):
    """Verify all matches are from the specified competition."""
    result = context['result']
    for match in result.data[:10]:
        assert match.get("competition") == competition, \
            f"Match should be from {competition}"


@then(parsers.parse('all matches should be from season {season:d}'))
def matches_from_season(context, season):
    """Verify all matches are from the specified season."""
    result = context['result']
    for match in result.data[:10]:
        assert match.get("season") == season, f"Match should be from {season}"


@then("the result should be empty")
def result_should_be_empty(context):
    """Verify that the result is empty."""
    result = context['result']
    assert result.count == 0, "Should return empty results"
