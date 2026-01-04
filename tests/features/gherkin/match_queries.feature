Feature: Match Queries
  As a user
  I want to search and filter soccer matches
  So that I can analyze match history

  Background:
    Given the match data is loaded

  # Find matches between teams
  Scenario: Find Fla-Flu derby matches
    When I search for matches between "Flamengo" and "Fluminense"
    Then I should receive matches
    And each match should have required fields

  Scenario: Find Palmeiras vs Corinthians derby matches
    When I search for matches between "Palmeiras" and "Corinthians"
    Then I should receive matches

  Scenario: Find Gre-Nal derby matches
    When I search for matches between "Gremio" and "Internacional"
    Then I should receive matches

  # Filter by competition
  Scenario: Filter Brasileirao matches
    When I filter for "brasileirao" competition matches
    Then I should receive matches
    And all matches should be from "brasileirao" competition

  Scenario: Filter Copa do Brasil matches
    When I filter for "copa_do_brasil" competition matches
    Then the query should succeed

  Scenario: Filter Libertadores matches
    When I filter for "libertadores" competition matches
    Then the query should succeed

  # Filter by season
  Scenario: Filter 2019 season matches
    When I filter for season 2019 matches
    Then I should receive matches
    And all matches should be from season 2019

  Scenario: Filter Flamengo 2019 matches
    When I search for "Flamengo" matches in season 2019
    Then I should receive matches

  # Team name variations
  Scenario: Search with team name including state suffix
    When I search for "Palmeiras-SP" matches
    Then the query should succeed

  Scenario: Search with team name without state suffix
    When I search for "Palmeiras" matches
    Then I should receive matches

  Scenario: Search with team name containing special characters
    When I search for "Sao Paulo" matches
    Then the query should succeed

  # Edge cases
  Scenario: Search for non-existent team
    When I search for "NonExistentTeam123" matches
    Then the query should succeed
    And the result should be empty

  Scenario: Search without any filters
    When I search for all matches with limit 50
    Then I should receive matches
