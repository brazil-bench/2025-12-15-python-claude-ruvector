"""
Brazilian Soccer MCP Server - Statistics Queries BDD Tests

This module contains pytest-bdd style test scenarios for statistical analysis.
Tests cover league standings calculations, biggest wins, averages, and head-to-head records.

Context:
- Calculates league standings from match results
- Identifies biggest wins and goal differences
- Computes statistical averages (goals per match, win rates)
- Analyzes head-to-head historical records
- Aggregates data across seasons and competitions

Data Sources:
- All match CSV files aggregated
- Calculated statistics from raw match data
"""

import pytest
from typing import List, Dict, Any


# Test Fixtures
@pytest.fixture
def loaded_data():
    """
    Fixture to provide loaded match data for statistics.

    Given: The match data is loaded from all CSV sources
    Returns: Dictionary containing all loaded match datasets
    """
    return {
        "matches": [],
        "seasons": []
    }


@pytest.fixture
def statistics_service(loaded_data):
    """
    Fixture to provide statistics calculation service.

    Given: A statistics service is initialized with match data
    Returns: StatisticsService instance for calculating statistics
    """
    class StatisticsService:
        def __init__(self, data):
            self.data = data

        def calculate_league_standings(self, season, competition="Brasileirão"):
            """Calculate league standings for a season"""
            return []

        def find_biggest_wins(self, limit=10, competition=None, season=None):
            """Find matches with largest goal differences"""
            return []

        def calculate_goals_per_match_average(self, competition=None, season=None):
            """Calculate average goals per match"""
            return 0.0

        def get_head_to_head_record(self, team1, team2, competition=None):
            """Get detailed head-to-head record"""
            return {}

        def calculate_home_advantage(self, season=None, competition=None):
            """Calculate home win/draw/loss percentages"""
            return {}

        def get_top_scorers(self, season, competition="Brasileirão"):
            """Get top scoring teams in a season"""
            return []

        def calculate_relegation_zone(self, season, competition="Brasileirão"):
            """Identify teams in relegation positions"""
            return []

    return StatisticsService(loaded_data)


# Test Scenarios

class TestCalculateLeagueStandings:
    """
    Feature: Calculate league standings

    As a user
    I want to see the league table for a season
    So that I can see which teams finished where
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I calculate 2019 Brasileirão standings",
            "then": "I should receive the complete table with Flamengo as champion",
            "season": 2019,
            "competition": "Brasileirão",
            "expected_champion": "Flamengo",
            "expected_teams": 20
        },
        {
            "given": "the match data is loaded",
            "when": "I calculate 2018 Brasileirão standings",
            "then": "I should receive standings sorted by points",
            "season": 2018,
            "competition": "Brasileirão",
            "expected_champion": "Palmeiras"
        },
        {
            "given": "the match data is loaded",
            "when": "I calculate 2023 standings",
            "then": "I should see points, wins, draws, losses, and goal difference",
            "season": 2023,
            "expected_fields": ["position", "team", "points", "wins", "draws",
                               "losses", "goals_for", "goals_against", "goal_difference"]
        }
    ])
    def test_calculate_league_standings(self, scenario, statistics_service):
        """
        Scenario: Calculate league standings

        Given the match data is loaded
        When I request standings for a specific season
        Then I should receive the complete league table
        And teams should be sorted by points (then goal difference)
        And each team should have complete statistics
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.calculate_league_standings(
            season=scenario["season"],
            competition=scenario.get("competition", "Brasileirão")
        )

        # Then
        assert isinstance(result, list), "Should return a list of standings"

        if "expected_teams" in scenario:
            assert len(result) == scenario["expected_teams"], \
                f"Should have {scenario['expected_teams']} teams"

        # Verify champion (first place)
        if "expected_champion" in scenario and len(result) > 0:
            champion = result[0]
            assert scenario["expected_champion"] in champion["team"], \
                f"{scenario['expected_champion']} should be champion"

        # Verify standings structure
        for i, standing in enumerate(result):
            assert isinstance(standing, dict), "Each standing should be a dict"

            if "expected_fields" in scenario:
                for field in scenario["expected_fields"]:
                    assert field in standing, f"Standing should have {field}"

            # Verify position matches index
            if "position" in standing:
                assert standing["position"] == i + 1, \
                    f"Position should be {i + 1}"

        # Verify sorting by points (descending)
        if len(result) > 1 and "points" in result[0]:
            points = [s["points"] for s in result]
            assert points == sorted(points, reverse=True) or \
                   all(points[i] >= points[i+1] or
                      (points[i] == points[i+1] and
                       result[i]["goal_difference"] >= result[i+1]["goal_difference"])
                      for i in range(len(points)-1)), \
                "Standings should be sorted by points then goal difference"


class TestFindBiggestWins:
    """
    Feature: Find biggest wins

    As a user
    I want to see the largest victories in the database
    So that I can identify dominant performances
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I request top 10 biggest wins",
            "then": "I should receive matches sorted by goal difference",
            "limit": 10,
            "expected_min_difference": 4
        },
        {
            "given": "the match data is loaded",
            "when": "I request biggest Brasileirão wins",
            "then": "I should receive only Brasileirão matches",
            "limit": 10,
            "competition": "Brasileirão"
        },
        {
            "given": "the match data is loaded",
            "when": "I request biggest wins in 2019",
            "then": "I should receive only 2019 matches",
            "limit": 5,
            "season": 2019
        }
    ])
    def test_find_biggest_wins(self, scenario, statistics_service):
        """
        Scenario: Find biggest wins

        Given the match data is loaded
        When I request the largest victories
        Then I should receive matches sorted by goal difference
        And each match should show the winning margin
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.find_biggest_wins(
            limit=scenario["limit"],
            competition=scenario.get("competition"),
            season=scenario.get("season")
        )

        # Then
        assert isinstance(result, list), "Should return a list of matches"
        assert len(result) <= scenario["limit"], \
            f"Should return at most {scenario['limit']} matches"
        assert len(result) > 0, "Should find biggest wins"

        for match in result:
            assert "home_team" in match, "Match should have home team"
            assert "away_team" in match, "Match should have away team"
            assert "home_goal" in match, "Match should have home goals"
            assert "away_goal" in match, "Match should have away goals"

            # Calculate goal difference
            goal_diff = abs(match["home_goal"] - match["away_goal"])
            assert goal_diff >= 0, "Goal difference should be non-negative"

        # Verify sorting by goal difference (descending)
        goal_diffs = [abs(m["home_goal"] - m["away_goal"]) for m in result]
        assert goal_diffs == sorted(goal_diffs, reverse=True), \
            "Matches should be sorted by goal difference (largest first)"

        if "expected_min_difference" in scenario:
            assert goal_diffs[0] >= scenario["expected_min_difference"], \
                f"Biggest win should have at least {scenario['expected_min_difference']} goal difference"


class TestCalculateAverages:
    """
    Feature: Calculate statistical averages

    As a user
    I want to see average statistics
    So that I can understand typical match outcomes
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I calculate average goals per match in Brasileirão",
            "then": "I should receive the goals per match average",
            "competition": "Brasileirão",
            "expected_range": (2.0, 3.5)
        },
        {
            "given": "the match data is loaded",
            "when": "I calculate average goals in 2019",
            "then": "I should receive season-specific average",
            "season": 2019,
            "expected_type": float
        },
        {
            "given": "the match data is loaded",
            "when": "I calculate overall average across all competitions",
            "then": "I should receive aggregated average",
            "all_competitions": True
        }
    ])
    def test_calculate_goals_per_match_average(self, scenario, statistics_service):
        """
        Scenario: Calculate goals per match average

        Given the match data is loaded
        When I request average goals per match
        Then I should receive a calculated average
        And the average should be within expected range
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.calculate_goals_per_match_average(
            competition=scenario.get("competition"),
            season=scenario.get("season")
        )

        # Then
        assert isinstance(result, (int, float)), \
            "Should return a numeric average"
        assert result >= 0, "Average should be non-negative"

        if "expected_range" in scenario:
            min_avg, max_avg = scenario["expected_range"]
            assert min_avg <= result <= max_avg, \
                f"Average should be between {min_avg} and {max_avg}"


class TestHeadToHeadRecords:
    """
    Feature: Calculate head-to-head records

    As a user
    I want to see detailed head-to-head statistics between two teams
    So that I can analyze historical matchups
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I get Flamengo vs Fluminense head-to-head",
            "then": "I should receive complete derby statistics",
            "team1": "Flamengo",
            "team2": "Fluminense",
            "expected_fields": ["team1_wins", "team2_wins", "draws", "total_matches",
                               "team1_goals", "team2_goals"]
        },
        {
            "given": "the match data is loaded",
            "when": "I get Palmeiras vs Corinthians all-time record",
            "then": "I should see wins, draws, and goals for each team",
            "team1": "Palmeiras",
            "team2": "Corinthians"
        },
        {
            "given": "the match data is loaded",
            "when": "I get head-to-head in Brasileirão only",
            "then": "I should receive competition-filtered statistics",
            "team1": "Grêmio",
            "team2": "Internacional",
            "competition": "Brasileirão"
        }
    ])
    def test_head_to_head_records(self, scenario, statistics_service):
        """
        Scenario: Calculate head-to-head records

        Given the match data is loaded
        When I request head-to-head statistics
        Then I should receive wins, draws, and goals for both teams
        And total matches should equal sum of wins and draws
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.get_head_to_head_record(
            team1=scenario["team1"],
            team2=scenario["team2"],
            competition=scenario.get("competition")
        )

        # Then
        assert isinstance(result, dict), "Should return head-to-head statistics"

        if "expected_fields" in scenario:
            for field in scenario["expected_fields"]:
                assert field in result, f"Result should have {field}"

        # Verify basic fields exist
        assert "team1_wins" in result or "wins" in result, \
            "Should have win statistics"
        assert "total_matches" in result or "matches" in result, \
            "Should have total matches"

        # Validate totals
        if all(k in result for k in ["team1_wins", "team2_wins", "draws", "total_matches"]):
            calculated_total = result["team1_wins"] + result["team2_wins"] + result["draws"]
            assert calculated_total == result["total_matches"], \
                "Total matches should equal sum of wins and draws"


class TestHomeAdvantageStatistics:
    """
    Feature: Calculate home advantage statistics

    As a user
    I want to see home vs away performance statistics
    So that I can quantify home field advantage
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I calculate home advantage in Brasileirão",
            "then": "I should receive home win/draw/loss percentages",
            "competition": "Brasileirão",
            "expected_fields": ["home_win_pct", "draw_pct", "away_win_pct"]
        },
        {
            "given": "the match data is loaded",
            "when": "I calculate home advantage in 2019",
            "then": "I should receive season-specific statistics",
            "season": 2019
        },
        {
            "given": "the match data is loaded",
            "when": "I compare home advantage across seasons",
            "then": "I should see if home advantage varies by year",
            "seasons": [2017, 2018, 2019]
        }
    ])
    def test_home_advantage_statistics(self, scenario, statistics_service):
        """
        Scenario: Calculate home advantage statistics

        Given the match data is loaded
        When I request home advantage statistics
        Then I should receive home/draw/away percentages
        And percentages should sum to 100%
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.calculate_home_advantage(
            season=scenario.get("season"),
            competition=scenario.get("competition")
        )

        # Then
        assert isinstance(result, dict), "Should return statistics dictionary"

        if "expected_fields" in scenario:
            for field in scenario["expected_fields"]:
                assert field in result, f"Result should have {field}"

        # Verify percentages
        if all(k in result for k in ["home_win_pct", "draw_pct", "away_win_pct"]):
            total_pct = (result["home_win_pct"] +
                        result["draw_pct"] +
                        result["away_win_pct"])
            assert abs(total_pct - 100.0) < 0.1, \
                "Percentages should sum to approximately 100%"


class TestTopScorersStatistics:
    """
    Feature: Identify top scoring teams

    As a user
    I want to see which teams scored the most goals
    So that I can identify the strongest attacking teams
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I get top scorers in 2019 Brasileirão",
            "then": "I should see teams ranked by goals scored",
            "season": 2019,
            "competition": "Brasileirão",
            "expected_top_team": "Flamengo"
        },
        {
            "given": "the match data is loaded",
            "when": "I get top 5 scoring teams in 2023",
            "then": "I should receive 5 teams with goal counts",
            "season": 2023,
            "limit": 5
        }
    ])
    def test_top_scorers_statistics(self, scenario, statistics_service):
        """
        Scenario: Identify top scoring teams

        Given the match data is loaded
        When I request top scoring teams
        Then I should receive teams sorted by goals scored
        And each team should have goal count and averages
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.get_top_scorers(
            season=scenario["season"],
            competition=scenario.get("competition", "Brasileirão")
        )

        # Then
        assert isinstance(result, list), "Should return list of teams"
        assert len(result) > 0, "Should find top scoring teams"

        for team in result:
            assert "team" in team or "name" in team, "Should have team name"
            assert "goals" in team or "goals_scored" in team, \
                "Should have goals scored"

        # Verify sorting by goals (descending)
        goals_key = "goals" if "goals" in result[0] else "goals_scored"
        goals = [t[goals_key] for t in result]
        assert goals == sorted(goals, reverse=True), \
            "Teams should be sorted by goals scored (highest first)"


class TestRelegationZoneAnalysis:
    """
    Feature: Identify teams in relegation zone

    As a user
    I want to see which teams were relegated
    So that I can analyze bottom-table performance
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I calculate relegation zone for 2019",
            "then": "I should see the bottom 4 teams",
            "season": 2019,
            "competition": "Brasileirão",
            "expected_count": 4
        },
        {
            "given": "the match data is loaded",
            "when": "I get relegation candidates in 2020",
            "then": "I should receive teams with fewest points",
            "season": 2020,
            "expected_position_range": (17, 20)
        }
    ])
    def test_relegation_zone_analysis(self, scenario, statistics_service):
        """
        Scenario: Identify teams in relegation zone

        Given the match data is loaded
        When I request relegation zone teams
        Then I should receive the bottom teams in the table
        And teams should be sorted by position
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.calculate_relegation_zone(
            season=scenario["season"],
            competition=scenario.get("competition", "Brasileirão")
        )

        # Then
        assert isinstance(result, list), "Should return list of teams"

        if "expected_count" in scenario:
            assert len(result) == scenario["expected_count"], \
                f"Should have {scenario['expected_count']} teams in relegation zone"

        for team in result:
            assert "team" in team or "name" in team, "Should have team name"
            assert "position" in team or "points" in team, \
                "Should have position or points"


class TestSeasonComparisonStatistics:
    """
    Feature: Compare statistics across seasons

    As a user
    I want to compare statistics across different seasons
    So that I can identify trends over time
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I compare goals per match across 2017-2020",
            "then": "I should see average goals for each season",
            "seasons": [2017, 2018, 2019, 2020],
            "metric": "goals_per_match"
        },
        {
            "given": "the match data is loaded",
            "when": "I compare home win rates across seasons",
            "then": "I should see if home advantage changed",
            "seasons": [2018, 2019, 2020],
            "metric": "home_win_rate"
        }
    ])
    def test_season_comparison_statistics(self, scenario, statistics_service):
        """
        Scenario: Compare statistics across seasons

        Given the match data is loaded
        When I request statistics for multiple seasons
        Then I should receive comparable data for each season
        And be able to identify trends
        """
        # Given
        assert statistics_service is not None

        # When
        results = {}
        for season in scenario["seasons"]:
            if scenario["metric"] == "goals_per_match":
                results[season] = statistics_service.calculate_goals_per_match_average(
                    season=season
                )
            elif scenario["metric"] == "home_win_rate":
                home_stats = statistics_service.calculate_home_advantage(
                    season=season
                )
                results[season] = home_stats.get("home_win_pct", 0)

        # Then
        assert len(results) == len(scenario["seasons"]), \
            "Should have data for all requested seasons"

        for season, value in results.items():
            assert isinstance(value, (int, float)), \
                f"Season {season} should have numeric value"
            assert value >= 0, f"Season {season} value should be non-negative"


class TestGoalDifferenceAnalysis:
    """
    Feature: Analyze goal differences

    As a user
    I want to analyze goal differences across teams
    So that I can identify dominant and struggling teams
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I get best goal difference in 2019",
            "then": "I should see Flamengo with highest goal difference",
            "season": 2019,
            "expected_leader": "Flamengo"
        },
        {
            "given": "the match data is loaded",
            "when": "I get worst goal difference in a season",
            "then": "I should identify the team with most negative difference",
            "season": 2020,
            "worst_difference": True
        }
    ])
    def test_goal_difference_analysis(self, scenario, statistics_service):
        """
        Scenario: Analyze goal differences

        Given the match data is loaded
        When I request goal difference statistics
        Then I should see teams ranked by goal difference
        And identify best and worst performing teams
        """
        # Given
        assert statistics_service is not None

        # When
        standings = statistics_service.calculate_league_standings(
            season=scenario["season"]
        )

        # Then
        assert isinstance(standings, list), "Should return standings"
        assert len(standings) > 0, "Should have team standings"

        for standing in standings:
            if "goal_difference" in standing:
                # Goal difference should be goals_for - goals_against
                if all(k in standing for k in ["goals_for", "goals_against"]):
                    expected_diff = standing["goals_for"] - standing["goals_against"]
                    assert standing["goal_difference"] == expected_diff, \
                        "Goal difference should be correctly calculated"


class TestMatchOutcomeDistribution:
    """
    Feature: Analyze match outcome distributions

    As a user
    I want to see the distribution of match outcomes
    So that I can understand result patterns
    """

    @pytest.mark.parametrize("scenario", [
        {
            "given": "the match data is loaded",
            "when": "I analyze outcome distribution in Brasileirão",
            "then": "I should see percentages of home wins, draws, away wins",
            "competition": "Brasileirão"
        },
        {
            "given": "the match data is loaded",
            "when": "I analyze high-scoring match frequency",
            "then": "I should see percentage of matches with 3+ goals",
            "min_goals": 3
        }
    ])
    def test_match_outcome_distribution(self, scenario, statistics_service):
        """
        Scenario: Analyze match outcome distributions

        Given the match data is loaded
        When I request outcome distribution statistics
        Then I should receive percentage breakdowns
        And understand common result patterns
        """
        # Given
        assert statistics_service is not None

        # When
        result = statistics_service.calculate_home_advantage(
            competition=scenario.get("competition")
        )

        # Then
        assert isinstance(result, dict), "Should return distribution statistics"

        # Verify we have outcome data
        if "home_win_pct" in result:
            assert 0 <= result["home_win_pct"] <= 100, \
                "Home win percentage should be 0-100%"
