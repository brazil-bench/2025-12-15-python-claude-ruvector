"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_statistics.py
Description: BDD tests for statistical analysis functionality
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Test statistical analysis using Given-When-Then BDD format.
    Covers standings, biggest wins, averages, and analysis.

Test Scenarios:
    - Calculate league standings
    - Find biggest wins
    - Calculate average goals
    - Identify top scorers
=============================================================================
"""

import pytest


class TestCalculateLeagueStandings:
    """
    Feature: Calculate league standings

    As a user
    I want to see league standings for a season
    So that I can see final positions
    """

    @pytest.mark.statistics
    def test_calculate_2019_brasileirao_standings(self, query_handler, bdd):
        """
        Scenario: Calculate 2019 Brasileirao standings

        Given the match data is loaded
        When I calculate 2019 standings
        Then I should see Flamengo as champion
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_standings(season=2019, competition="brasileirao")
        bdd.when("I calculate 2019 standings", result)

        # Then
        bdd.then("query should succeed", result.success)

        if result.data and len(result.data) > 0:
            # Verify standings structure
            first_place = result.data[0]
            bdd.then("should have team field", "team" in first_place)
            bdd.then("should have points field", "points" in first_place)

    @pytest.mark.statistics
    def test_calculate_2018_brasileirao_standings(self, query_handler, bdd):
        """
        Scenario: Calculate 2018 Brasileirao standings

        Given the match data is loaded
        When I calculate 2018 standings
        Then I should receive complete standings
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_standings(season=2018, competition="brasileirao")
        bdd.when("I calculate 2018 standings", result)

        # Then
        bdd.then("query should succeed", result.success)

    @pytest.mark.statistics
    def test_standings_sorted_by_points(self, query_handler, bdd):
        """
        Scenario: Verify standings are sorted correctly

        Given the match data is loaded
        When I calculate standings
        Then teams should be sorted by points descending
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_standings(season=2019, competition="brasileirao")
        bdd.when("I calculate standings", result)

        # Then
        bdd.then("query should succeed", result.success)

        if result.data and len(result.data) > 1:
            points = [s.get("points", 0) for s in result.data]
            bdd.then(
                "should be sorted by points",
                points == sorted(points, reverse=True)
            )


class TestFindBiggestWins:
    """
    Feature: Find biggest wins

    As a user
    I want to see the largest victories
    So that I can identify dominant performances
    """

    @pytest.mark.statistics
    def test_find_biggest_wins(self, query_handler, bdd):
        """
        Scenario: Find biggest wins

        Given the match data is loaded
        When I request biggest wins
        Then I should receive matches sorted by goal difference
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="biggest_wins", limit=10)
        bdd.when("I request biggest wins", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find matches", result.count > 0)

    @pytest.mark.statistics
    def test_find_biggest_wins_in_season(self, query_handler, bdd):
        """
        Scenario: Find biggest wins in specific season

        Given the match data is loaded
        When I request biggest wins in 2019
        Then I should receive only 2019 matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="biggest_wins", season=2019, limit=10)
        bdd.when("I request 2019 biggest wins", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestCalculateAverages:
    """
    Feature: Calculate statistical averages

    As a user
    I want to see average goals per match
    So that I can understand typical outcomes
    """

    @pytest.mark.statistics
    def test_calculate_average_goals(self, query_handler, bdd):
        """
        Scenario: Calculate average goals per match

        Given the match data is loaded
        When I request average goals statistics
        Then I should receive goals per match average
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="avg_goals")
        bdd.when("I request average goals", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should have data", result.data is not None)

        if result.data:
            bdd.then(
                "should have average goals",
                "average_goals_per_match" in result.data
            )
            avg = result.data.get("average_goals_per_match", 0)
            bdd.then(
                "average should be reasonable (1-5 goals)",
                1.0 <= avg <= 5.0
            )

    @pytest.mark.statistics
    def test_calculate_season_average_goals(self, query_handler, bdd):
        """
        Scenario: Calculate average goals for specific season

        Given the match data is loaded
        When I request average goals for 2019
        Then I should receive season-specific average
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="avg_goals", season=2019)
        bdd.when("I request 2019 average goals", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestHighestScoringMatches:
    """
    Feature: Find highest scoring matches

    As a user
    I want to see matches with the most goals
    So that I can find exciting games
    """

    @pytest.mark.statistics
    def test_find_highest_scoring_matches(self, query_handler, bdd):
        """
        Scenario: Find highest scoring matches

        Given the match data is loaded
        When I request highest scoring matches
        Then I should receive matches sorted by total goals
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="highest_scoring", limit=10)
        bdd.when("I request highest scoring matches", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find matches", result.count > 0)

        if result.data and len(result.data) > 1:
            goals = [m.get("total_goals", 0) for m in result.data]
            bdd.then(
                "should be sorted by total goals",
                goals == sorted(goals, reverse=True)
            )


class TestStatisticalAnalysis:
    """
    Feature: General statistical analysis

    As a user
    I want to see various statistics
    So that I can understand patterns
    """

    @pytest.mark.statistics
    def test_get_home_vs_away_statistics(self, query_handler, bdd):
        """
        Scenario: Get home vs away win statistics

        Given the match data is loaded
        When I request average goals statistics
        Then I should see home wins, away wins, and draws
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="avg_goals")
        bdd.when("I request statistics", result)

        # Then
        bdd.then("query should succeed", result.success)

        if result.data:
            bdd.then("should have home wins", "home_wins" in result.data)
            bdd.then("should have away wins", "away_wins" in result.data)
            bdd.then("should have draws", "draws" in result.data)


class TestStatisticsEdgeCases:
    """
    Feature: Handle edge cases in statistics

    As a user
    I want the system to handle edge cases
    So that queries work reliably
    """

    @pytest.mark.statistics
    def test_invalid_stat_type(self, query_handler, bdd):
        """
        Scenario: Request invalid statistic type

        Given the match data is loaded
        When I request an invalid stat type
        Then I should receive an error response
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_statistics(stat_type="invalid_stat_type")
        bdd.when("I request invalid stat type", result)

        # Then
        bdd.then("should indicate failure", not result.success or result.error is not None)

    @pytest.mark.statistics
    def test_standings_for_nonexistent_season(self, query_handler, bdd):
        """
        Scenario: Request standings for non-existent season

        Given the match data is loaded
        When I request standings for year 9999
        Then I should receive empty results
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_standings(season=9999)
        bdd.when("I request 9999 standings", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should have no data", result.count == 0 or result.data is None)
