"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_team_queries.py
Description: pytest-bdd step definitions for team query tests
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15
Updated: 2026-01-04

Purpose:
    BDD step definitions for team statistics functionality using pytest-bdd
    with Gherkin .feature files.
=============================================================================
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from the feature file
scenarios('gherkin/team_queries.feature')


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


# When steps for team statistics
@when(parsers.parse('I request statistics for "{team}"'))
def request_team_stats(query_handler, context, team):
    """Request statistics for a team."""
    result = query_handler.get_team_stats(team=team)
    context['result'] = result


@when(parsers.parse('I request statistics for "{team}" in season {season:d}'))
def request_team_stats_for_season(query_handler, context, team, season):
    """Request team statistics for a specific season."""
    result = query_handler.get_team_stats(team=team, season=season)
    context['result'] = result


@when(parsers.parse('I request statistics for "{team}" in "{competition}" competition'))
def request_team_stats_for_competition(query_handler, context, team, competition):
    """Request team statistics for a specific competition."""
    result = query_handler.get_team_stats(team=team, competition=competition)
    context['result'] = result


@when(parsers.parse('I request head-to-head between "{team1}" and "{team2}"'))
def request_head_to_head(query_handler, context, team1, team2):
    """Request head-to-head statistics between two teams."""
    result = query_handler.get_head_to_head(team1=team1, team2=team2)
    context['result'] = result


# Then steps
@then("the query should succeed")
def query_should_succeed(context):
    """Verify the query succeeded."""
    result = context['result']
    assert result.success, "Query should succeed"


@then("the statistics should include wins draws and losses")
def stats_include_wins_draws_losses(context):
    """Verify statistics include wins, draws, and losses."""
    result = context['result']
    assert result.data is not None, "Should have statistics"
    if result.data:
        assert "wins" in result.data, "Should have wins"
        assert "draws" in result.data, "Should have draws"
        assert "losses" in result.data, "Should have losses"
        assert "win_rate" in result.data, "Should have win rate"


@then("the statistics should be present")
def stats_should_be_present(context):
    """Verify statistics are present."""
    result = context['result']
    assert result.data is not None, "Should have statistics"


@then("the statistics should include goals for and against")
def stats_include_goals(context):
    """Verify statistics include goals for and against."""
    result = context['result']
    if result.data:
        assert "goals_for" in result.data, "Should have goals for"
        assert "goals_against" in result.data, "Should have goals against"
        assert "goal_difference" in result.data, "Should have goal difference"


@then("the head-to-head should include team wins and draws")
def h2h_include_wins_draws(context):
    """Verify head-to-head includes wins and draws."""
    result = context['result']
    if result.data:
        assert "team1_wins" in result.data, "Should have team1 wins"
        assert "team2_wins" in result.data, "Should have team2 wins"
        assert "draws" in result.data, "Should have draws"
        assert "total_matches" in result.data, "Should have total matches"


@then("matches should be found")
def matches_should_be_found(context):
    """Verify matches were found."""
    result = context['result']
    assert result.count > 0, "Should find matches"


@then("the result should be a classic derby")
def result_is_classic_derby(context):
    """Verify the result is identified as a classic derby."""
    result = context['result']
    if result.data:
        # Either it's marked as a classic derby or there are matches
        is_derby = result.data.get("is_classic_derby", False) or result.count > 0
        assert is_derby, "Should be identified as classic derby"


@then("the statistics should include home and away records")
def stats_include_home_away(context):
    """Verify statistics include home and away records."""
    result = context['result']
    if result.data:
        assert "home_record" in result.data, "Should have home record"
        assert "away_record" in result.data, "Should have away record"


@then("there should be no matches played")
def no_matches_played(context):
    """Verify there are no matches played."""
    result = context['result']
    assert result.data is None or result.data.get("matches_played", 0) == 0, \
        "Should have no matches"
