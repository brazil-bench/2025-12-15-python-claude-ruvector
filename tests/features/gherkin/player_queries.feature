Feature: Player Queries
  As a user
  I want to search and filter players
  So that I can find specific player information

  Background:
    Given the player data is loaded

  # Search by name
  Scenario: Search for Neymar
    When I search for player "Neymar"
    Then I should find players
    And the results should include "Neymar"

  Scenario: Search for Messi
    When I search for player "Messi"
    Then I should find players

  Scenario: Search with partial name
    When I search for player "Gabriel"
    Then the query should succeed

  # Filter by nationality
  Scenario: Filter Brazilian players
    When I filter players by nationality "Brazil"
    Then I should find players
    And all players should be from "Brazil"

  Scenario: Filter Argentine players
    When I filter players by nationality "Argentina"
    Then I should find players

  # Filter by club
  Scenario: Filter Flamengo players
    When I filter players by club "Flamengo"
    Then the query should succeed

  Scenario: Filter Barcelona players
    When I filter players by club "Barcelona"
    Then the query should succeed

  # Filter by position
  Scenario: Filter strikers
    When I filter players by position "ST"
    Then the query should succeed

  Scenario: Filter goalkeepers
    When I filter players by position "GK"
    Then the query should succeed

  # Top rated players
  Scenario: Get top Brazilian players
    When I search for "Brazil" players with minimum rating 80
    Then I should find players
    And players should be sorted by rating descending

  Scenario: Get top overall players
    When I search for players with minimum rating 90
    Then the query should succeed
    And all players should have rating 90 or above

  # Edge cases
  Scenario: Search for non-existent player
    When I search for player "ZZZNonExistentPlayer123"
    Then the query should succeed
    And the result should be empty

  Scenario: Case-insensitive player search
    When I search for player "messi"
    Then the query should succeed
