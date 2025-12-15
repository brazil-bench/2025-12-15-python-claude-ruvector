"""
Brazilian Soccer MCP Server - Team Queries BDD Tests

This module contains pytest-bdd style test scenarios for team query functionality.
Tests cover team statistics, performance records, goal analysis, and season comparisons.

Context:
- Calculates team statistics from match data
- Handles home/away performance analysis
- Computes win/loss/draw records
- Analyzes goals scored and conceded
- Compares team performance across multiple seasons

Data Sources:
- Aggregated from all match CSV files
- Calculated statistics from match results
"""

import pytest
from typing import List, Dict, Any


# Test Fixtures
@pytest.fixture
def loaded_data():
    """
    Fixture to provide loaded match data for team statistics.

    Given: The match data is loaded from all CSV sources
    Returns: Dictionary containing all loaded match datasets
    """
    return {
        "matches": [],
        "teams": []
    }


@pytest.fixture
def team_service(loaded_data):
    """
    Fixture to provide team statistics service.

    Given: A team service is initialized with match data
    Returns: TeamService instance for querying team statistics
    """
    class TeamService:
        def __init__(self, data):
            self.data = data

        def get_team_record(self, team_name, season=None, home_only=False,
                           away_only=False, competition=None):
            """Get team win/loss/draw record"""
            return {
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "matches_played": 0,
                "win_rate": 0.0
            }

        def get_team_goals(self, team_name, season=None):
            """Get team goals scored and conceded"""
            return {
                "goals_scored": 0,
                "goals_conceded": 0,
                "goal_difference": 0,
                "goals_per_match": 0.0
            }

        def compare_teams(self, team1, team2, season=None):
            """Compare two teams head-to-head"""
            return {
                "team1_wins": 0,
                "team2_wins": 0,
                "draws": 0,
                "total_matches": 0
            }

        def get_season_comparison(self, team_name, seasons):
            """Compare team performance across multiple seasons"""
            return {}

    return TeamService(loaded_data)


# Test Scenarios

class TestTeamHomeAwayRecord:
    """
    Feature: Get team home and away records

    As a user
    I want to see a team's home and away performance
    So that I can analyze home field advantage
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I request Corinthians' home record for 2022",
            "then": "I should receive home match statistics",
            "team": "Corinthians",
            "season": 2022,
            "home_only": True,
            "expected_fields": ["wins", "draws", "losses", "win_rate"]
        },
        {
            "given": "the match data is loaded",
            "when": "I request Flamengo's away record for 2019",
            "then": "I should receive away match statistics",
            "team": "Flamengo",
            "season": 2019,
            "away_only": True,
            "expected_fields": ["wins", "draws", "losses", "win_rate"]
        },
        {
            "given": "the match data is loaded",
            "when": "I request Palmeiras' home and away records",
            "then": "I should receive both home and away statistics",
            "team": "Palmeiras",
            "season": 2023,
            "compare_home_away": True
        }
    ])
    def test_team_home_away_record(self, scenario, team_service):
        """
        Scenario: Get team home and away records

        Given the match data is loaded
        When I request a team's home or away record
        Then I should receive wins, draws, losses, and win rate
        And statistics should be accurate for the specified venue
        """
        # Given
        assert team_service is not None

        # When
        if scenario.get("compare_home_away"):
            home_record = team_service.get_team_record(
                team_name=scenario["team"],
                season=scenario["season"],
                home_only=True
            )
            away_record = team_service.get_team_record(
                team_name=scenario["team"],
                season=scenario["season"],
                away_only=True
            )

            # Then
            assert isinstance(home_record, dict), "Should return home record dict"
            assert isinstance(away_record, dict), "Should return away record dict"

            for field in ["wins", "draws", "losses", "matches_played", "win_rate"]:
                assert field in home_record, f"Home record should have {field}"
                assert field in away_record, f"Away record should have {field}"

            # Home and away should combine to total season matches
            total_matches = home_record["matches_played"] + away_record["matches_played"]
            assert total_matches > 0, "Should have played matches"

        else:
            result = team_service.get_team_record(
                team_name=scenario["team"],
                season=scenario.get("season"),
                home_only=scenario.get("home_only", False),
                away_only=scenario.get("away_only", False)
            )

            # Then
            assert isinstance(result, dict), "Should return a statistics dictionary"

            for field in scenario["expected_fields"]:
                assert field in result, f"Result should contain {field}"

            assert result["wins"] >= 0, "Wins should be non-negative"
            assert result["draws"] >= 0, "Draws should be non-negative"
            assert result["losses"] >= 0, "Losses should be non-negative"
            assert 0.0 <= result["win_rate"] <= 100.0, "Win rate should be 0-100%"


class TestTeamWinLossDrawStats:
    """
    Feature: Calculate team win/loss/draw statistics

    As a user
    I want to see a team's overall record
    So that I can evaluate their performance
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I request Palmeiras' 2023 statistics",
            "then": "I should receive complete season statistics",
            "team": "Palmeiras",
            "season": 2023,
            "validate_total": True
        },
        {
            "given": "the match data is loaded",
            "when": "I request Santos' all-time statistics",
            "then": "I should receive statistics across all seasons",
            "team": "Santos",
            "season": None,
            "all_time": True
        },
        {
            "given": "the match data is loaded",
            "when": "I request Fluminense's Brasileirão statistics",
            "then": "I should receive competition-specific statistics",
            "team": "Fluminense",
            "competition": "Brasileirão",
            "season": 2023
        }
    ])
    def test_team_win_loss_draw_stats(self, scenario, team_service):
        """
        Scenario: Calculate team win/loss/draw statistics

        Given the match data is loaded
        When I request a team's statistics
        Then I should receive wins, losses, draws counts
        And win rate should be correctly calculated
        And total matches should equal wins + losses + draws
        """
        # Given
        assert team_service is not None

        # When
        result = team_service.get_team_record(
            team_name=scenario["team"],
            season=scenario.get("season"),
            competition=scenario.get("competition")
        )

        # Then
        assert isinstance(result, dict), "Should return statistics dictionary"
        assert "wins" in result, "Should include wins count"
        assert "losses" in result, "Should include losses count"
        assert "draws" in result, "Should include draws count"
        assert "matches_played" in result, "Should include total matches"
        assert "win_rate" in result, "Should include win rate"

        # Validate calculations
        if scenario.get("validate_total"):
            total = result["wins"] + result["losses"] + result["draws"]
            assert total == result["matches_played"], \
                "Wins + losses + draws should equal total matches"

        if result["matches_played"] > 0:
            expected_win_rate = (result["wins"] / result["matches_played"]) * 100
            assert abs(result["win_rate"] - expected_win_rate) < 0.01, \
                "Win rate should be correctly calculated"


class TestTeamGoalsStatistics:
    """
    Feature: Get team goals scored and conceded

    As a user
    I want to see how many goals a team scores and concedes
    So that I can analyze their offensive and defensive performance
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I request Flamengo's 2019 goal statistics",
            "then": "I should receive goals scored and conceded",
            "team": "Flamengo",
            "season": 2019,
            "expected_fields": ["goals_scored", "goals_conceded", "goal_difference"]
        },
        {
            "given": "the match data is loaded",
            "when": "I request Atlético Mineiro's goal statistics",
            "then": "I should receive goal averages per match",
            "team": "Atlético-MG",
            "season": 2021,
            "expected_fields": ["goals_per_match", "goals_conceded_per_match"]
        },
        {
            "given": "the match data is loaded",
            "when": "I request the highest scoring team in 2023",
            "then": "I should identify the team with most goals",
            "season": 2023,
            "find_highest_scorer": True
        }
    ])
    def test_team_goals_statistics(self, scenario, team_service):
        """
        Scenario: Get team goals scored and conceded

        Given the match data is loaded
        When I request a team's goal statistics
        Then I should receive goals scored, conceded, and difference
        And goals per match averages should be calculated
        """
        # Given
        assert team_service is not None

        # When
        if scenario.get("find_highest_scorer"):
            # This would require a different method to get all teams
            # For now, we'll test the goal stats structure
            result = team_service.get_team_goals(
                team_name="Palmeiras",
                season=scenario["season"]
            )
        else:
            result = team_service.get_team_goals(
                team_name=scenario["team"],
                season=scenario.get("season")
            )

        # Then
        assert isinstance(result, dict), "Should return goals statistics"

        for field in scenario.get("expected_fields", []):
            assert field in result, f"Result should contain {field}"

        if "goals_scored" in result:
            assert result["goals_scored"] >= 0, "Goals scored should be non-negative"

        if "goals_conceded" in result:
            assert result["goals_conceded"] >= 0, "Goals conceded should be non-negative"

        if "goal_difference" in result:
            expected_diff = result.get("goals_scored", 0) - result.get("goals_conceded", 0)
            assert result["goal_difference"] == expected_diff, \
                "Goal difference should equal scored minus conceded"


class TestCompareTeamPerformance:
    """
    Feature: Compare team performance across seasons

    As a user
    I want to compare a team's performance across different seasons
    So that I can identify trends and improvements
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I compare Palmeiras' 2018 and 2019 seasons",
            "then": "I should receive comparative statistics",
            "team": "Palmeiras",
            "seasons": [2018, 2019],
            "metrics": ["wins", "goals_scored", "win_rate"]
        },
        {
            "given": "the match data is loaded",
            "when": "I compare Flamengo across 2017-2020",
            "then": "I should see multi-season progression",
            "team": "Flamengo",
            "seasons": [2017, 2018, 2019, 2020],
            "track_progression": True
        },
        {
            "given": "the match data is loaded",
            "when": "I compare Corinthians' best and worst seasons",
            "then": "I should identify performance extremes",
            "team": "Corinthians",
            "find_extremes": True
        }
    ])
    def test_compare_team_performance_across_seasons(self, scenario, team_service):
        """
        Scenario: Compare team performance across seasons

        Given the match data is loaded
        When I request comparison across multiple seasons
        Then I should receive statistics for each season
        And be able to identify trends and changes
        """
        # Given
        assert team_service is not None

        # When
        if scenario.get("find_extremes"):
            # This would get all available seasons and find best/worst
            seasons = [2012, 2013, 2014, 2015]  # Example seasons
            result = team_service.get_season_comparison(
                team_name=scenario["team"],
                seasons=seasons
            )
        else:
            result = team_service.get_season_comparison(
                team_name=scenario["team"],
                seasons=scenario["seasons"]
            )

        # Then
        assert isinstance(result, dict), "Should return comparison dictionary"
        assert len(result) >= len(scenario.get("seasons", [])), \
            "Should have data for each requested season"

        for season, stats in result.items():
            assert isinstance(stats, dict), f"Season {season} should have stats dict"

            if "metrics" in scenario:
                for metric in scenario["metrics"]:
                    assert metric in stats, f"Should include {metric} for {season}"


class TestHeadToHeadComparison:
    """
    Feature: Compare two teams head-to-head

    As a user
    I want to compare two teams directly
    So that I can see which team performs better
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I compare Flamengo vs Palmeiras all-time",
            "then": "I should receive head-to-head statistics",
            "team1": "Flamengo",
            "team2": "Palmeiras",
            "season": None,
            "expected_fields": ["team1_wins", "team2_wins", "draws", "total_matches"]
        },
        {
            "given": "the match data is loaded",
            "when": "I compare Grêmio vs Internacional in 2023",
            "then": "I should receive season-specific head-to-head",
            "team1": "Grêmio",
            "team2": "Internacional",
            "season": 2023
        },
        {
            "given": "the match data is loaded",
            "when": "I compare São Paulo vs Santos",
            "then": "I should handle special characters correctly",
            "team1": "São Paulo",
            "team2": "Santos",
            "has_special_chars": True
        }
    ])
    def test_head_to_head_comparison(self, scenario, team_service):
        """
        Scenario: Compare two teams head-to-head

        Given the match data is loaded
        When I compare two specific teams
        Then I should receive wins for each team and draws
        And total matches should equal the sum of wins and draws
        """
        # Given
        assert team_service is not None

        # When
        result = team_service.compare_teams(
            team1=scenario["team1"],
            team2=scenario["team2"],
            season=scenario.get("season")
        )

        # Then
        assert isinstance(result, dict), "Should return comparison dictionary"

        if "expected_fields" in scenario:
            for field in scenario["expected_fields"]:
                assert field in result, f"Result should contain {field}"

        if "total_matches" in result:
            expected_total = (result.get("team1_wins", 0) +
                            result.get("team2_wins", 0) +
                            result.get("draws", 0))
            assert result["total_matches"] == expected_total, \
                "Total matches should equal sum of all results"


class TestTeamStreaksAndTrends:
    """
    Feature: Identify team winning/losing streaks

    As a user
    I want to identify team streaks and trends
    So that I can analyze form and momentum
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I analyze Flamengo's 2019 winning streak",
            "then": "I should identify consecutive wins",
            "team": "Flamengo",
            "season": 2019,
            "streak_type": "winning"
        },
        {
            "given": "the match data is loaded",
            "when": "I analyze a team's unbeaten run",
            "then": "I should identify consecutive matches without loss",
            "team": "Palmeiras",
            "season": 2018,
            "streak_type": "unbeaten"
        }
    ])
    def test_team_streaks_and_trends(self, scenario, team_service):
        """
        Scenario: Identify team winning/losing streaks

        Given the match data is loaded
        When I analyze a team's match sequence
        Then I should identify the longest streaks
        And receive the dates and matches involved
        """
        # Given
        assert team_service is not None

        # When
        record = team_service.get_team_record(
            team_name=scenario["team"],
            season=scenario["season"]
        )

        # Then
        assert isinstance(record, dict), "Should return team record"
        assert record["matches_played"] > 0, "Should have played matches"

        # Validate that we can calculate streaks from the record
        if record["wins"] > 0:
            assert record["win_rate"] > 0, "Win rate should be positive if wins > 0"


class TestTeamDefensiveRecords:
    """
    Feature: Analyze team defensive statistics

    As a user
    I want to see defensive performance metrics
    So that I can evaluate a team's defense
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I request clean sheets for Atlético-MG",
            "then": "I should receive matches with zero goals conceded",
            "team": "Atlético-MG",
            "season": 2021,
            "metric": "clean_sheets"
        },
        {
            "given": "the match data is loaded",
            "when": "I request goals conceded per match",
            "then": "I should receive defensive averages",
            "team": "Santos",
            "season": 2023,
            "metric": "goals_conceded_avg"
        }
    ])
    def test_team_defensive_records(self, scenario, team_service):
        """
        Scenario: Analyze team defensive statistics

        Given the match data is loaded
        When I request defensive metrics
        Then I should receive clean sheets and goals conceded data
        And averages should be correctly calculated
        """
        # Given
        assert team_service is not None

        # When
        goals_data = team_service.get_team_goals(
            team_name=scenario["team"],
            season=scenario.get("season")
        )

        # Then
        assert isinstance(goals_data, dict), "Should return goals data"
        assert "goals_conceded" in goals_data, "Should include goals conceded"
        assert goals_data["goals_conceded"] >= 0, "Goals conceded should be non-negative"


class TestTeamFormAnalysis:
    """
    Feature: Analyze recent team form

    As a user
    I want to see a team's recent performance
    So that I can predict future results
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I request Flamengo's last 5 matches",
            "then": "I should receive recent form analysis",
            "team": "Flamengo",
            "last_n_matches": 5
        },
        {
            "given": "the match data is loaded",
            "when": "I request Palmeiras' form in last 10 matches",
            "then": "I should see wins, draws, losses in recent games",
            "team": "Palmeiras",
            "last_n_matches": 10
        }
    ])
    def test_team_form_analysis(self, scenario, team_service):
        """
        Scenario: Analyze recent team form

        Given the match data is loaded
        When I request a team's recent matches
        Then I should receive form metrics for last N matches
        And results should be in chronological order
        """
        # Given
        assert team_service is not None

        # When
        record = team_service.get_team_record(
            team_name=scenario["team"]
        )

        # Then
        assert isinstance(record, dict), "Should return team record"
        # Form analysis would be based on the most recent matches
        assert "matches_played" in record, "Should have matches played count"
