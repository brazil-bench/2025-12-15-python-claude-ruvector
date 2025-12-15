"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_match_queries.py
Description: BDD tests for match query functionality
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Test match query functionality using Given-When-Then BDD format.
    Covers finding matches by team, competition, date range, and season.

Test Scenarios:
    - Find matches between two specific teams
    - Filter matches by competition
    - Filter matches by season
    - Filter matches by date range
    - Handle team name variations
=============================================================================
"""

import pytest
from datetime import datetime


class TestFindMatchesBetweenTeams:
    """
    Feature: Find matches between two teams

    As a user
    I want to find all matches between two teams
    So that I can see their head-to-head history
    """

    @pytest.mark.match_queries
    def test_find_flamengo_vs_fluminense_matches(self, query_handler, bdd):
        """
        Scenario: Find Fla-Flu derby matches

        Given the match data is loaded
        When I search for matches between Flamengo and Fluminense
        Then I should receive a list of derby matches
        And each match should have date, scores, and competition
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Flamengo", opponent="Fluminense", limit=50)
        bdd.when("I search for matches between Flamengo and Fluminense", result)

        # Then
        bdd.then("I should receive matches", result.success)
        bdd.then("matches should be found", result.count > 0)

        for match in result.data[:5]:
            bdd.then(
                "match should have required fields",
                all(k in match for k in ["date", "home_team", "away_team", "score"])
            )

    @pytest.mark.match_queries
    def test_find_palmeiras_vs_corinthians_matches(self, query_handler, bdd):
        """
        Scenario: Find Palmeiras vs Corinthians derby matches

        Given the match data is loaded
        When I search for matches between Palmeiras and Corinthians
        Then I should receive a list of classic derby matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Palmeiras", opponent="Corinthians", limit=50)
        bdd.when("I search for matches between Palmeiras and Corinthians", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find derby matches", result.count > 0)

    @pytest.mark.match_queries
    def test_find_gremio_vs_internacional_matches(self, query_handler, bdd):
        """
        Scenario: Find Gre-Nal derby matches

        Given the match data is loaded
        When I search for matches between Gremio and Internacional
        Then I should receive a list of Gre-Nal matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Gremio", opponent="Internacional", limit=50)
        bdd.when("I search for Gre-Nal matches", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find Gre-Nal matches", result.count > 0)


class TestFilterMatchesByCompetition:
    """
    Feature: Filter matches by competition

    As a user
    I want to filter matches by competition
    So that I can analyze competition-specific data
    """

    @pytest.mark.match_queries
    def test_filter_brasileirao_matches(self, query_handler, bdd):
        """
        Scenario: Filter Brasileirao matches

        Given the match data is loaded
        When I filter for Brasileirao matches
        Then I should receive only Serie A matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(competition="brasileirao", limit=100)
        bdd.when("I filter for Brasileirao matches", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find Brasileirao matches", result.count > 0)

        for match in result.data[:10]:
            bdd.then(
                "match should be from Brasileirao",
                match.get("competition") == "brasileirao"
            )

    @pytest.mark.match_queries
    def test_filter_copa_do_brasil_matches(self, query_handler, bdd):
        """
        Scenario: Filter Copa do Brasil matches

        Given the match data is loaded
        When I filter for Copa do Brasil matches
        Then I should receive only cup matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(competition="copa_do_brasil", limit=50)
        bdd.when("I filter for Copa do Brasil matches", result)

        # Then
        bdd.then("query should succeed", result.success)

    @pytest.mark.match_queries
    def test_filter_libertadores_matches(self, query_handler, bdd):
        """
        Scenario: Filter Copa Libertadores matches

        Given the match data is loaded
        When I filter for Libertadores matches
        Then I should receive only continental matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(competition="libertadores", limit=50)
        bdd.when("I filter for Libertadores matches", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestFilterMatchesBySeason:
    """
    Feature: Filter matches by season

    As a user
    I want to filter matches by season
    So that I can analyze season-specific data
    """

    @pytest.mark.match_queries
    def test_filter_2019_season_matches(self, query_handler, bdd):
        """
        Scenario: Filter 2019 season matches

        Given the match data is loaded
        When I filter for 2019 season matches
        Then I should receive only 2019 matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(season=2019, limit=100)
        bdd.when("I filter for 2019 matches", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find 2019 matches", result.count > 0)

        for match in result.data[:10]:
            bdd.then(
                "match should be from 2019",
                match.get("season") == 2019
            )

    @pytest.mark.match_queries
    def test_filter_flamengo_2019_matches(self, query_handler, bdd):
        """
        Scenario: Filter Flamengo's 2019 season matches

        Given the match data is loaded
        When I filter for Flamengo matches in 2019
        Then I should receive Flamengo's championship season matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Flamengo", season=2019, limit=50)
        bdd.when("I filter for Flamengo 2019 matches", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find Flamengo matches", result.count > 0)


class TestTeamNameVariations:
    """
    Feature: Handle team name variations

    As a user
    I want the system to handle different team name formats
    So that I can find matches regardless of naming conventions
    """

    @pytest.mark.match_queries
    def test_team_name_with_state_suffix(self, query_handler, bdd):
        """
        Scenario: Search with team name including state suffix

        Given the match data is loaded
        When I search for "Palmeiras-SP"
        Then I should receive Palmeiras matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Palmeiras-SP", limit=20)
        bdd.when("I search for Palmeiras-SP", result)

        # Then
        bdd.then("query should succeed", result.success)

    @pytest.mark.match_queries
    def test_team_name_without_state_suffix(self, query_handler, bdd):
        """
        Scenario: Search with team name without state suffix

        Given the match data is loaded
        When I search for "Palmeiras"
        Then I should receive Palmeiras matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Palmeiras", limit=20)
        bdd.when("I search for Palmeiras", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find matches", result.count > 0)

    @pytest.mark.match_queries
    def test_team_with_special_characters(self, query_handler, bdd):
        """
        Scenario: Search with team name containing special characters

        Given the match data is loaded
        When I search for "Sao Paulo" (with or without accent)
        Then I should receive Sao Paulo matches
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="Sao Paulo", limit=20)
        bdd.when("I search for Sao Paulo", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestMatchQueryEdgeCases:
    """
    Feature: Handle edge cases in match queries

    As a user
    I want the system to handle edge cases gracefully
    So that queries work reliably
    """

    @pytest.mark.match_queries
    def test_nonexistent_team(self, query_handler, bdd):
        """
        Scenario: Search for non-existent team

        Given the match data is loaded
        When I search for a team that doesn't exist
        Then I should receive an empty result
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(team="NonExistentTeam123", limit=20)
        bdd.when("I search for non-existent team", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should return empty results", result.count == 0)

    @pytest.mark.match_queries
    def test_empty_search(self, query_handler, bdd):
        """
        Scenario: Search with no filters

        Given the match data is loaded
        When I search without any filters
        Then I should receive all matches (up to limit)
        """
        # Given
        bdd.given("the match data is loaded", query_handler is not None)

        # When
        result = query_handler.search_matches(limit=50)
        bdd.when("I search without filters", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should return matches", result.count > 0)
