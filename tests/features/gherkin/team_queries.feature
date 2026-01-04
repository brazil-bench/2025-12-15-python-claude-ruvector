Feature: Team Queries
  As a user
  I want to see team statistics and comparisons
  So that I can evaluate team performance

  Background:
    Given the match data is loaded

  # Team statistics
  Scenario: Get Palmeiras statistics
    When I request statistics for "Palmeiras"
    Then the query should succeed
    And the statistics should include wins draws and losses

  Scenario: Get Flamengo 2019 championship statistics
    When I request statistics for "Flamengo" in season 2019
    Then the query should succeed
    And the statistics should be present

  Scenario: Get Corinthians Brasileirao statistics
    When I request statistics for "Corinthians" in "brasileirao" competition
    Then the query should succeed

  # Goals statistics
  Scenario: Get team goals statistics
    When I request statistics for "Santos"
    Then the query should succeed
    And the statistics should include goals for and against

  # Head to head
  Scenario: Get Flamengo vs Fluminense head-to-head
    When I request head-to-head between "Flamengo" and "Fluminense"
    Then the query should succeed
    And the head-to-head should include team wins and draws

  Scenario: Get Gremio vs Internacional head-to-head
    When I request head-to-head between "Gremio" and "Internacional"
    Then the query should succeed
    And matches should be found

  Scenario: Identify classic derby in head-to-head
    When I request head-to-head between "Palmeiras" and "Corinthians"
    Then the query should succeed
    And the result should be a classic derby

  # Home and away records
  Scenario: Get home and away records
    When I request statistics for "Flamengo" in season 2019
    Then the query should succeed
    And the statistics should include home and away records

  # Edge cases
  Scenario: Get statistics for non-existent team
    When I request statistics for "NonExistentTeam123"
    Then the query should succeed
    And there should be no matches played

  Scenario: Request head-to-head with same team
    When I request head-to-head between "Flamengo" and "Flamengo"
    Then the query should succeed
