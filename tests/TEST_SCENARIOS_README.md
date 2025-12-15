# Brazilian Soccer MCP Server - BDD Test Scenarios

## Overview

This directory contains comprehensive BDD (Behavior-Driven Development) test scenarios for the Brazilian Soccer MCP Server. Tests are organized using the **Given-When-Then** (GWT) pattern and implemented with pytest-bdd style.

## Test Philosophy

### BDD Structure
All tests follow the Given-When-Then pattern:

- **Given**: Initial context and preconditions
- **When**: The action or event being tested
- **Then**: Expected outcomes and assertions

### Example Scenario
```python
@pytest.mark.parametrize("scenario", [
    {
        "given": "the match data is loaded",
        "when": "I search for matches between 'Flamengo' and 'Fluminense'",
        "then": "I should receive a list of Fla-Flu derby matches",
        "team1": "Flamengo",
        "team2": "Fluminense",
        "expected_min_matches": 1
    }
])
def test_find_matches_between_teams(self, scenario, match_service):
    # Given
    assert match_service is not None

    # When
    result = match_service.search_matches(
        team1=scenario["team1"],
        team2=scenario["team2"]
    )

    # Then
    assert len(result) >= scenario["expected_min_matches"]
    assert all(has_required_fields(m) for m in result)
```

## Test Files

### 1. test_match_queries.py
**Purpose**: Test match search and filtering capabilities

**Test Classes**:
- `TestFindMatchesBetweenTwoTeams`: Search for matches between specific teams
- `TestFindMatchesByDateRange`: Filter matches by date ranges
- `TestFindMatchesByCompetition`: Filter by competition (Brasileirão, Copa do Brasil, Libertadores)
- `TestFindMatchesBySeason`: Filter matches by season/year
- `TestFindDerbyMatches`: Find classic derby matches (Fla-Flu, Grenal, etc.)
- `TestMatchQueryEdgeCases`: Handle team name variations and special characters
- `TestCombinedMatchFilters`: Combine multiple search criteria

**Total Scenarios**: 25+

**Key Features Tested**:
- Team name normalization (handling "Flamengo" vs "Flamengo-RJ")
- Date format handling (ISO, Brazilian, with time)
- UTF-8 encoding for special characters (São Paulo, Grêmio, Avaí)
- Derby rivalry recognition
- Multi-criteria filtering

**Sample Scenarios**:
```gherkin
Scenario: Find matches between two teams
  Given the match data is loaded
  When I search for matches between "Flamengo" and "Fluminense"
  Then I should receive a list of matches
  And each match should have date, scores, and competition

Scenario: Find derby matches
  Given the match data is loaded
  When I search for "Fla-Flu" derby matches
  Then I should receive Flamengo vs Fluminense matches
  And matches should include head-to-head statistics
```

### 2. test_team_queries.py
**Purpose**: Test team statistics and performance analysis

**Test Classes**:
- `TestTeamHomeAwayRecord`: Analyze home vs away performance
- `TestTeamWinLossDrawStats`: Calculate win/loss/draw records
- `TestTeamGoalsStatistics`: Track goals scored and conceded
- `TestCompareTeamPerformance`: Compare team performance across seasons
- `TestHeadToHeadComparison`: Direct team comparisons
- `TestTeamStreaksAndTrends`: Identify winning/losing streaks
- `TestTeamDefensiveRecords`: Analyze defensive metrics (clean sheets, etc.)
- `TestTeamFormAnalysis`: Recent form analysis (last N matches)

**Total Scenarios**: 30+

**Key Features Tested**:
- Home field advantage calculation
- Win rate percentages
- Goals per match averages
- Goal difference calculations
- Multi-season comparisons
- Head-to-head records
- Clean sheets tracking
- Recent form (last 5, 10 matches)

**Sample Scenarios**:
```gherkin
Scenario: Get team home record
  Given the match data is loaded
  When I request Corinthians' home record for 2022
  Then I should receive home match statistics
  And statistics should include wins, draws, losses, and win rate

Scenario: Compare team performance across seasons
  Given the match data is loaded
  When I compare Palmeiras' 2018 and 2019 seasons
  Then I should receive comparative statistics
  And see metrics like wins, goals scored, and win rate
```

### 3. test_player_queries.py
**Purpose**: Test player search and analysis

**Test Classes**:
- `TestSearchPlayerByName`: Search players by name (partial/exact matching)
- `TestFilterPlayersByNationality`: Filter by nationality (focus on Brazilian players)
- `TestFilterPlayersByClub`: Filter by club affiliation
- `TestGetTopRatedPlayers`: Get highest-rated players with filters
- `TestPlayerAttributeQueries`: Access detailed player attributes and skills
- `TestBrazilianPlayersAtBrazilianClubs`: Find Brazilian talent at Brazilian clubs
- `TestPlayerPositionQueries`: Query players by position (ST, GK, etc.)
- `TestPlayerAgeAndPotential`: Filter by age and potential ratings
- `TestPlayerSearchEdgeCases`: Handle edge cases in player searches

**Total Scenarios**: 28+

**Key Features Tested**:
- Partial and exact name matching
- Case-insensitive search
- Nationality filtering
- Club filtering with partial matching
- Position-based queries
- Rating and potential thresholds
- Special character handling in names
- Brazilian club identification
- Age range filtering

**Sample Scenarios**:
```gherkin
Scenario: Search player by name
  Given the player data is loaded
  When I search for "Neymar"
  Then I should find Neymar Jr's player record
  And record should have nationality, club, position, and rating

Scenario: Filter players by nationality
  Given the player data is loaded
  When I filter for Brazilian players
  Then I should receive all Brazilian players
  And all players should have nationality "Brazil"

Scenario: Get top-rated players
  Given the player data is loaded
  When I request top 10 Brazilian players
  Then I should receive the 10 highest-rated Brazilians
  And players should be sorted by rating descending
```

### 4. test_statistics.py
**Purpose**: Test statistical analysis and aggregations

**Test Classes**:
- `TestCalculateLeagueStandings`: Calculate league tables from match results
- `TestFindBiggestWins`: Identify largest victories by goal difference
- `TestCalculateAverages`: Compute statistical averages (goals per match)
- `TestHeadToHeadRecords`: Detailed head-to-head statistics
- `TestHomeAdvantageStatistics`: Quantify home field advantage
- `TestTopScorersStatistics`: Identify highest-scoring teams
- `TestRelegationZoneAnalysis`: Track bottom-table teams
- `TestSeasonComparisonStatistics`: Compare statistics across seasons
- `TestGoalDifferenceAnalysis`: Analyze goal differences
- `TestMatchOutcomeDistribution`: Distribution of match outcomes

**Total Scenarios**: 32+

**Key Features Tested**:
- League standings calculation (points, goal difference)
- Sorting by points and tiebreaker rules
- Biggest wins identification
- Average goals per match
- Home/draw/away percentages
- Top scorers ranking
- Relegation zone (bottom 4 teams)
- Multi-season trends
- Goal difference rankings
- Outcome distribution percentages

**Sample Scenarios**:
```gherkin
Scenario: Calculate league standings
  Given the match data is loaded
  When I calculate 2019 Brasileirão standings
  Then I should receive the complete table with Flamengo as champion
  And teams should be sorted by points then goal difference
  And each team should have wins, draws, losses, goals

Scenario: Find biggest wins
  Given the match data is loaded
  When I request top 10 biggest wins
  Then I should receive matches sorted by goal difference
  And each match should show the winning margin

Scenario: Calculate home advantage
  Given the match data is loaded
  When I calculate home advantage in Brasileirão
  Then I should receive home win/draw/away percentages
  And percentages should sum to 100%
```

## Test Fixtures

### Shared Fixtures (conftest.py)

#### Data Fixtures
- `data_loader`: Session-scoped fixture with all loaded CSV data
- `query_handler`: QueryHandler instance for running queries
- `vector_store`: VectorStore for semantic search tests
- `sample_matches`: Sample match data for unit tests
- `sample_players`: Sample player data for unit tests

#### Service Fixtures
Each test file uses service-specific fixtures:
- `match_service`: For match query operations
- `team_service`: For team statistics operations
- `player_service`: For player query operations
- `statistics_service`: For statistical calculations

#### Helper Classes
- `GivenWhenThen`: BDD scenario helper for explicit GWT testing

## Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_match_queries.py
pytest tests/test_team_queries.py
pytest tests/test_player_queries.py
pytest tests/test_statistics.py
```

### Run Specific Test Class
```bash
pytest tests/test_match_queries.py::TestFindMatchesBetweenTwoTeams
pytest tests/test_team_queries.py::TestTeamHomeAwayRecord
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src/brazilian_soccer_mcp --cov-report=html
```

### Run Specific Markers
```bash
pytest tests/ -m match_queries
pytest tests/ -m team_queries
pytest tests/ -m player_queries
pytest tests/ -m statistics
```

### Run with BDD Output
```bash
pytest tests/ -v --tb=short
```

## Test Markers

Tests are marked with categories for selective execution:

- `@pytest.mark.match_queries`: Match query tests
- `@pytest.mark.team_queries`: Team query tests
- `@pytest.mark.player_queries`: Player query tests
- `@pytest.mark.statistics`: Statistical analysis tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

## Test Coverage

### Match Queries (test_match_queries.py)
- ✅ Find matches between two teams
- ✅ Find matches by date range
- ✅ Find matches by competition
- ✅ Find matches by season
- ✅ Find derby matches (Fla-Flu, Grenal, Clássico Paulista, Choque-Rei)
- ✅ Handle team name variations (with/without state suffixes)
- ✅ Handle special characters (São Paulo, Grêmio)
- ✅ Combine multiple filters
- ✅ Handle edge cases (non-existent teams, invalid inputs)

### Team Queries (test_team_queries.py)
- ✅ Get team home record
- ✅ Get team away record
- ✅ Calculate win/loss/draw statistics
- ✅ Get goals scored and conceded
- ✅ Calculate goal difference
- ✅ Compare teams head-to-head
- ✅ Compare performance across seasons
- ✅ Identify winning/losing streaks
- ✅ Track clean sheets
- ✅ Analyze recent form (last N matches)

### Player Queries (test_player_queries.py)
- ✅ Search by player name (partial/exact)
- ✅ Filter by nationality
- ✅ Filter by club
- ✅ Get top-rated players
- ✅ Filter by position
- ✅ Filter by age and potential
- ✅ Find Brazilian players at Brazilian clubs
- ✅ Handle special characters in names
- ✅ Case-insensitive search
- ✅ Handle non-existent players

### Statistics (test_statistics.py)
- ✅ Calculate league standings
- ✅ Find biggest wins
- ✅ Calculate goals per match average
- ✅ Get head-to-head records
- ✅ Calculate home advantage
- ✅ Identify top scorers
- ✅ Calculate relegation zone
- ✅ Compare statistics across seasons
- ✅ Analyze goal differences
- ✅ Calculate match outcome distribution

## Data Sources

Tests use data from:
- `Brasileirao_Matches.csv` (4,180 matches)
- `Brazilian_Cup_Matches.csv` (1,337 matches)
- `Libertadores_Matches.csv` (1,255 matches)
- `BR-Football-Dataset.csv` (10,296 matches)
- `novo_campeonato_brasileiro.csv` (6,886 matches)
- `fifa_data.csv` (18,207 players)

## Test Data Characteristics

### Team Name Variations
Tests handle multiple naming formats:
- With state: "Palmeiras-SP", "Flamengo-RJ"
- Without state: "Palmeiras", "Flamengo"
- Full names: "Sport Club Corinthians Paulista"

### Date Formats
Tests handle multiple date formats:
- ISO: "2023-09-24"
- Brazilian: "29/03/2003"
- With time: "2012-05-19 18:30:00"

### Special Characters
Tests properly handle UTF-8:
- Accents: São Paulo, Grêmio, Avaí
- Cedilla: Fortaleza Esporte Clube

## Classic Derbies Tested

1. **Fla-Flu**: Flamengo vs Fluminense (Rio de Janeiro)
2. **Clássico Paulista**: Corinthians vs Palmeiras (São Paulo)
3. **Grenal**: Grêmio vs Internacional (Porto Alegre)
4. **Choque-Rei**: Palmeiras vs São Paulo (São Paulo)
5. **San-São**: Santos vs São Paulo (São Paulo)
6. **Clássico das Multidões**: Corinthians vs Palmeiras (São Paulo)

## Expected Test Results

### Success Criteria
- All scenarios pass with loaded data
- Proper handling of team name variations
- Correct UTF-8 encoding for special characters
- Accurate statistical calculations
- Proper sorting and ranking
- Edge case handling

### Performance Expectations
- Simple lookups: < 2 seconds
- Aggregate queries: < 5 seconds
- Statistics calculations: < 10 seconds
- No timeout errors

## Contributing

When adding new test scenarios:

1. Follow the Given-When-Then pattern
2. Use parametrized scenarios for variations
3. Include descriptive scenario dictionaries
4. Add appropriate test markers
5. Update this README with new scenarios
6. Ensure tests are independent and idempotent

## Example Test Output

```
tests/test_match_queries.py::TestFindMatchesBetweenTwoTeams::test_find_matches_between_teams[scenario0] PASSED
tests/test_match_queries.py::TestFindMatchesByDateRange::test_find_matches_by_date_range[scenario0] PASSED
tests/test_team_queries.py::TestTeamHomeAwayRecord::test_team_home_away_record[scenario0] PASSED
tests/test_player_queries.py::TestSearchPlayerByName::test_search_player_by_name[scenario0] PASSED
tests/test_statistics.py::TestCalculateLeagueStandings::test_calculate_league_standings[scenario0] PASSED

========================= 115 passed in 12.34s =========================
```

## Future Enhancements

Potential additional test scenarios:
- Player transfer history
- Manager/coach statistics
- Stadium-specific statistics
- Weather impact on matches
- Referee statistics
- Injury tracking
- Form predictions
- Derby intensity metrics
- Fan attendance correlation
- Time-of-day performance analysis

## License

These tests are part of the Brazilian Soccer MCP Server project.
Test data sources maintain their original licenses:
- CC BY 4.0 (Kaggle datasets)
- Apache 2.0 (FIFA player data)
- CC0 Public Domain (BR Football Dataset)
