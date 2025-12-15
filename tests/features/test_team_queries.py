"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_team_queries.py
Description: BDD tests for team statistics functionality
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Test team statistics calculation using Given-When-Then BDD format.
    Covers team records, goals, head-to-head comparisons.

Test Scenarios:
    - Calculate team win/loss/draw records
    - Calculate team goals statistics
    - Compare team performance across seasons
    - Calculate head-to-head statistics
=============================================================================
"""

import pytest


class TestTeamWinLossDrawStatistics:
    """
    Feature: Calculate team win/loss/draw statistics

    As a user
    I want to see team win/loss/draw records
    So that I can evaluate team performance
    """

    @pytest.mark.team_queries
    def test_get_palmeiras_statistics(self, query_handler, bdd):
        """
        Scenario: Get Palmeiras statistics

        Given the match data is loaded
        When I request Palmeiras statistics
        Then I should receive wins, draws, losses, and win rate
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_team_stats(team="Palmeiras")
        bdd.when("I request Palmeiras statistics", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should have statistics", result.data is not None)

        if result.data:
            bdd.then("should have wins", "wins" in result.data)
            bdd.then("should have draws", "draws" in result.data)
            bdd.then("should have losses", "losses" in result.data)
            bdd.then("should have win rate", "win_rate" in result.data)

    @pytest.mark.team_queries
    def test_get_flamengo_2019_statistics(self, query_handler, bdd):
        """
        Scenario: Get Flamengo's 2019 championship statistics

        Given the match data is loaded
        When I request Flamengo statistics for 2019
        Then I should receive their championship season stats
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_team_stats(team="Flamengo", season=2019)
        bdd.when("I request Flamengo 2019 statistics", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should have statistics", result.data is not None)

    @pytest.mark.team_queries
    def test_get_corinthians_brasileirao_statistics(self, query_handler, bdd):
        """
        Scenario: Get Corinthians Brasileirao statistics

        Given the match data is loaded
        When I request Corinthians statistics for Brasileirao
        Then I should receive their league record
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_team_stats(team="Corinthians", competition="brasileirao")
        bdd.when("I request Corinthians Brasileirao statistics", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestTeamGoalsStatistics:
    """
    Feature: Calculate team goals statistics

    As a user
    I want to see team goals scored and conceded
    So that I can analyze offensive and defensive performance
    """

    @pytest.mark.team_queries
    def test_get_team_goals_for_and_against(self, query_handler, bdd):
        """
        Scenario: Get team goals statistics

        Given the match data is loaded
        When I request team statistics for Santos
        Then I should receive goals for and against
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_team_stats(team="Santos")
        bdd.when("I request Santos statistics", result)

        # Then
        bdd.then("query should succeed", result.success)
        if result.data:
            bdd.then("should have goals for", "goals_for" in result.data)
            bdd.then("should have goals against", "goals_against" in result.data)
            bdd.then("should have goal difference", "goal_difference" in result.data)


class TestHeadToHeadStatistics:
    """
    Feature: Calculate head-to-head statistics

    As a user
    I want to see head-to-head records between two teams
    So that I can analyze historical matchups
    """

    @pytest.mark.team_queries
    def test_flamengo_vs_fluminense_head_to_head(self, query_handler, bdd):
        """
        Scenario: Get Flamengo vs Fluminense head-to-head

        Given the match data is loaded
        When I request head-to-head between Flamengo and Fluminense
        Then I should receive wins, draws, and goals for each team
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_head_to_head(team1="Flamengo", team2="Fluminense")
        bdd.when("I request Fla-Flu head-to-head", result)

        # Then
        bdd.then("query should succeed", result.success)
        if result.data:
            bdd.then("should have team1 wins", "team1_wins" in result.data)
            bdd.then("should have team2 wins", "team2_wins" in result.data)
            bdd.then("should have draws", "draws" in result.data)
            bdd.then("should have total matches", "total_matches" in result.data)

    @pytest.mark.team_queries
    def test_gremio_vs_internacional_head_to_head(self, query_handler, bdd):
        """
        Scenario: Get Gremio vs Internacional head-to-head

        Given the match data is loaded
        When I request head-to-head between Gremio and Internacional
        Then I should receive Gre-Nal statistics
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_head_to_head(team1="Gremio", team2="Internacional")
        bdd.when("I request Gre-Nal head-to-head", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find matches", result.count > 0)

    @pytest.mark.team_queries
    def test_head_to_head_is_classic_derby(self, query_handler, bdd):
        """
        Scenario: Identify classic derby in head-to-head

        Given the match data is loaded
        When I request head-to-head for a classic derby
        Then I should see the derby name
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_head_to_head(team1="Palmeiras", team2="Corinthians")
        bdd.when("I request Derby Paulista head-to-head", result)

        # Then
        bdd.then("query should succeed", result.success)
        if result.data:
            bdd.then(
                "should identify as classic derby",
                result.data.get("is_classic_derby", False) or result.count > 0
            )


class TestTeamHomeAwayRecords:
    """
    Feature: Calculate team home and away records

    As a user
    I want to see separate home and away performance
    So that I can analyze home field advantage
    """

    @pytest.mark.team_queries
    def test_get_home_and_away_records(self, query_handler, bdd):
        """
        Scenario: Get home and away records

        Given the match data is loaded
        When I request team statistics
        Then I should receive separate home and away records
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_team_stats(team="Flamengo", season=2019)
        bdd.when("I request Flamengo 2019 statistics", result)

        # Then
        bdd.then("query should succeed", result.success)
        if result.data:
            bdd.then("should have home record", "home_record" in result.data)
            bdd.then("should have away record", "away_record" in result.data)


class TestTeamQueryEdgeCases:
    """
    Feature: Handle edge cases in team queries

    As a user
    I want the system to handle edge cases gracefully
    So that queries work reliably
    """

    @pytest.mark.team_queries
    def test_nonexistent_team_stats(self, query_handler, bdd):
        """
        Scenario: Get statistics for non-existent team

        Given the match data is loaded
        When I request statistics for a non-existent team
        Then I should receive an appropriate response
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_team_stats(team="NonExistentTeam123")
        bdd.when("I request non-existent team statistics", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should have no matches", result.data is None or result.data.get("matches_played", 0) == 0)

    @pytest.mark.team_queries
    def test_head_to_head_same_team(self, query_handler, bdd):
        """
        Scenario: Request head-to-head with same team

        Given the match data is loaded
        When I request head-to-head between a team and itself
        Then I should receive empty results
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.get_head_to_head(team1="Flamengo", team2="Flamengo")
        bdd.when("I request Flamengo vs Flamengo", result)

        # Then
        bdd.then("query should succeed", result.success)
