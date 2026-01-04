"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_statistics.py
Description: pytest-bdd step definitions for statistics tests
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15
Updated: 2026-01-04

Purpose:
    BDD step definitions for statistical analysis functionality using pytest-bdd
    with Gherkin .feature files.
=============================================================================
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the feature file
scenarios('gherkin/statistics.feature')


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


# When steps for statistics
@when(parsers.parse('I calculate standings for season {season:d} competition "{competition}"'))
def calculate_standings(query_handler, context, season, competition):
    """Calculate standings for a season and competition."""
    result = query_handler.get_standings(season=season, competition=competition)
    context['result'] = result


@when(parsers.parse('I request "{stat_type}" statistics'))
def request_statistics(query_handler, context, stat_type):
    """Request a specific type of statistics."""
    result = query_handler.get_statistics(stat_type=stat_type, limit=10)
    context['result'] = result


@when(parsers.parse('I request "{stat_type}" statistics for season {season:d}'))
def request_statistics_for_season(query_handler, context, stat_type, season):
    """Request statistics for a specific season."""
    result = query_handler.get_statistics(stat_type=stat_type, season=season, limit=10)
    context['result'] = result


# Then steps
@then("the query should succeed")
def query_should_succeed(context):
    """Verify the query succeeded."""
    result = context['result']
    assert result.success, "Query should succeed"


@then("the standings should have team and points fields")
def standings_have_fields(context):
    """Verify standings have required fields."""
    result = context['result']
    if result.data and len(result.data) > 0:
        first_place = result.data[0]
        assert "team" in first_place, "Should have team field"
        assert "points" in first_place, "Should have points field"


@then("standings should be sorted by points descending")
def standings_sorted_by_points(context):
    """Verify standings are sorted by points descending."""
    result = context['result']
    if result.data and len(result.data) > 1:
        points = [s.get("points", 0) for s in result.data]
        assert points == sorted(points, reverse=True), \
            "Standings should be sorted by points"


@then("I should receive matches")
def should_receive_matches(context):
    """Verify that matches were returned."""
    result = context['result']
    assert result.success, "Query should succeed"
    assert result.count > 0, "Should find matches"


@then("the average goals should be between 1 and 5")
def average_goals_reasonable(context):
    """Verify average goals is reasonable."""
    result = context['result']
    assert result.data is not None, "Should have data"
    if result.data:
        assert "average_goals_per_match" in result.data, "Should have average goals"
        avg = result.data.get("average_goals_per_match", 0)
        assert 1.0 <= avg <= 5.0, "Average should be reasonable (1-5 goals)"


@then("matches should be sorted by total goals descending")
def matches_sorted_by_goals(context):
    """Verify matches are sorted by total goals descending."""
    result = context['result']
    if result.data and len(result.data) > 1:
        goals = [m.get("total_goals", 0) for m in result.data]
        assert goals == sorted(goals, reverse=True), \
            "Matches should be sorted by total goals"


@then("the statistics should include home wins away wins and draws")
def stats_include_home_away_draws(context):
    """Verify statistics include home wins, away wins, and draws."""
    result = context['result']
    if result.data:
        assert "home_wins" in result.data, "Should have home wins"
        assert "away_wins" in result.data, "Should have away wins"
        assert "draws" in result.data, "Should have draws"


@then("the request should indicate failure")
def request_should_fail(context):
    """Verify the request indicates failure."""
    result = context['result']
    assert not result.success or hasattr(result, 'error') and result.error is not None, \
        "Should indicate failure"


@then("the result should be empty")
def result_should_be_empty(context):
    """Verify the result is empty."""
    result = context['result']
    assert result.count == 0 or result.data is None, "Should have no data"
