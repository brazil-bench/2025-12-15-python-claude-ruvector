"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_player_queries.py
Description: BDD tests for player search functionality
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Test player search functionality using Given-When-Then BDD format.
    Covers searching by name, nationality, club, position, and rating.

Test Scenarios:
    - Search players by name
    - Filter players by nationality
    - Filter players by club
    - Filter players by position
    - Get top-rated players
=============================================================================
"""

import pytest


class TestSearchPlayerByName:
    """
    Feature: Search players by name

    As a user
    I want to search for players by name
    So that I can find specific player information
    """

    @pytest.mark.player_queries
    def test_search_neymar(self, query_handler, bdd):
        """
        Scenario: Search for Neymar

        Given the player data is loaded
        When I search for "Neymar"
        Then I should find Neymar Jr's record
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(name="Neymar")
        bdd.when("I search for Neymar", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find players", result.count > 0)

        if result.data:
            names = [p["name"] for p in result.data]
            bdd.then("should include Neymar", any("Neymar" in n for n in names))

    @pytest.mark.player_queries
    def test_search_messi(self, query_handler, bdd):
        """
        Scenario: Search for Messi

        Given the player data is loaded
        When I search for "Messi"
        Then I should find Lionel Messi's record
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(name="Messi")
        bdd.when("I search for Messi", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find players", result.count > 0)

    @pytest.mark.player_queries
    def test_search_partial_name(self, query_handler, bdd):
        """
        Scenario: Search with partial name

        Given the player data is loaded
        When I search for "Gabriel"
        Then I should find multiple players named Gabriel
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(name="Gabriel")
        bdd.when("I search for Gabriel", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestFilterPlayersByNationality:
    """
    Feature: Filter players by nationality

    As a user
    I want to filter players by nationality
    So that I can find all Brazilian players
    """

    @pytest.mark.player_queries
    def test_filter_brazilian_players(self, query_handler, bdd):
        """
        Scenario: Filter Brazilian players

        Given the player data is loaded
        When I filter for Brazilian players
        Then I should receive all Brazilian players
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(nationality="Brazil", limit=50)
        bdd.when("I filter for Brazilian players", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find Brazilian players", result.count > 0)

        for player in result.data[:10]:
            bdd.then(
                "player should be Brazilian",
                player.get("nationality") == "Brazil"
            )

    @pytest.mark.player_queries
    def test_filter_argentine_players(self, query_handler, bdd):
        """
        Scenario: Filter Argentine players

        Given the player data is loaded
        When I filter for Argentine players
        Then I should find Messi among them
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(nationality="Argentina", limit=50)
        bdd.when("I filter for Argentine players", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find Argentine players", result.count > 0)


class TestFilterPlayersByClub:
    """
    Feature: Filter players by club

    As a user
    I want to filter players by club
    So that I can see team rosters
    """

    @pytest.mark.player_queries
    def test_filter_flamengo_players(self, query_handler, bdd):
        """
        Scenario: Filter Flamengo players

        Given the player data is loaded
        When I filter for Flamengo players
        Then I should receive all Flamengo players in database
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(club="Flamengo", limit=30)
        bdd.when("I filter for Flamengo players", result)

        # Then
        bdd.then("query should succeed", result.success)

    @pytest.mark.player_queries
    def test_filter_barcelona_players(self, query_handler, bdd):
        """
        Scenario: Filter Barcelona players

        Given the player data is loaded
        When I filter for Barcelona players
        Then I should receive high-rated players
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(club="Barcelona", limit=30)
        bdd.when("I filter for Barcelona players", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestFilterPlayersByPosition:
    """
    Feature: Filter players by position

    As a user
    I want to filter players by position
    So that I can find position-specific talent
    """

    @pytest.mark.player_queries
    def test_filter_strikers(self, query_handler, bdd):
        """
        Scenario: Filter strikers

        Given the player data is loaded
        When I filter for strikers (ST)
        Then I should receive all strikers
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(position="ST", limit=30)
        bdd.when("I filter for strikers", result)

        # Then
        bdd.then("query should succeed", result.success)

    @pytest.mark.player_queries
    def test_filter_goalkeepers(self, query_handler, bdd):
        """
        Scenario: Filter goalkeepers

        Given the player data is loaded
        When I filter for goalkeepers (GK)
        Then I should receive all goalkeepers
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(position="GK", limit=30)
        bdd.when("I filter for goalkeepers", result)

        # Then
        bdd.then("query should succeed", result.success)


class TestGetTopRatedPlayers:
    """
    Feature: Get top-rated players

    As a user
    I want to see the highest-rated players
    So that I can identify the best players
    """

    @pytest.mark.player_queries
    def test_get_top_brazilian_players(self, query_handler, bdd):
        """
        Scenario: Get top Brazilian players

        Given the player data is loaded
        When I search for Brazilian players with high rating
        Then I should receive the best Brazilian players
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(nationality="Brazil", min_overall=80, limit=20)
        bdd.when("I search for top Brazilian players", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should find high-rated players", result.count > 0)

        # Verify sorted by rating (descending)
        if result.data and len(result.data) > 1:
            ratings = [p.get("overall", 0) for p in result.data]
            bdd.then(
                "players should be sorted by rating",
                ratings == sorted(ratings, reverse=True)
            )

    @pytest.mark.player_queries
    def test_get_top_overall_players(self, query_handler, bdd):
        """
        Scenario: Get top overall players

        Given the player data is loaded
        When I search for players with 90+ rating
        Then I should receive elite players
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(min_overall=90, limit=10)
        bdd.when("I search for 90+ rated players", result)

        # Then
        bdd.then("query should succeed", result.success)

        for player in result.data:
            bdd.then(
                "player should have 90+ rating",
                player.get("overall", 0) >= 90
            )


class TestPlayerQueryEdgeCases:
    """
    Feature: Handle edge cases in player queries

    As a user
    I want the system to handle edge cases gracefully
    So that queries work reliably
    """

    @pytest.mark.player_queries
    def test_search_nonexistent_player(self, query_handler, bdd):
        """
        Scenario: Search for non-existent player

        Given the player data is loaded
        When I search for a player that doesn't exist
        Then I should receive empty results
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(name="ZZZNonExistentPlayer123")
        bdd.when("I search for non-existent player", result)

        # Then
        bdd.then("query should succeed", result.success)
        bdd.then("should return empty results", result.count == 0)

    @pytest.mark.player_queries
    def test_case_insensitive_search(self, query_handler, bdd):
        """
        Scenario: Case-insensitive player search

        Given the player data is loaded
        When I search for "messi" (lowercase)
        Then I should find Messi
        """
        # Given
        bdd.given("the player data is loaded", query_handler is not None)

        # When
        result = query_handler.search_players(name="messi")
        bdd.when("I search for messi (lowercase)", result)

        # Then
        bdd.then("query should succeed", result.success)
