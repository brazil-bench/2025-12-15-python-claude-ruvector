Feature: Statistics
  As a user
  I want to see various statistics about matches
  So that I can understand patterns and results

  Background:
    Given the match data is loaded

  # League standings
  Scenario: Calculate 2019 Brasileirao standings
    When I calculate standings for season 2019 competition "brasileirao"
    Then the query should succeed
    And the standings should have team and points fields

  Scenario: Calculate 2018 Brasileirao standings
    When I calculate standings for season 2018 competition "brasileirao"
    Then the query should succeed

  Scenario: Verify standings are sorted correctly
    When I calculate standings for season 2019 competition "brasileirao"
    Then the query should succeed
    And standings should be sorted by points descending

  # Biggest wins
  Scenario: Find biggest wins
    When I request "biggest_wins" statistics
    Then I should receive matches

  Scenario: Find biggest wins in 2019
    When I request "biggest_wins" statistics for season 2019
    Then the query should succeed

  # Average goals
  Scenario: Calculate average goals per match
    When I request "avg_goals" statistics
    Then the query should succeed
    And the average goals should be between 1 and 5

  Scenario: Calculate average goals for 2019
    When I request "avg_goals" statistics for season 2019
    Then the query should succeed

  # Highest scoring matches
  Scenario: Find highest scoring matches
    When I request "highest_scoring" statistics
    Then I should receive matches
    And matches should be sorted by total goals descending

  # Home vs away statistics
  Scenario: Get home vs away win statistics
    When I request "avg_goals" statistics
    Then the query should succeed
    And the statistics should include home wins away wins and draws

  # Edge cases
  Scenario: Request invalid statistic type
    When I request "invalid_stat_type" statistics
    Then the request should indicate failure

  Scenario: Request standings for non-existent season
    When I calculate standings for season 9999 competition "brasileirao"
    Then the query should succeed
    And the result should be empty
