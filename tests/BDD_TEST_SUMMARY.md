# BDD Test Scenarios Summary - Brazilian Soccer MCP Server

## Overview

This document provides a comprehensive summary of all BDD (Behavior-Driven Development) test scenarios designed for the Brazilian Soccer MCP server. Tests follow the Given-When-Then pattern and cover all major functionality areas.

## Total Test Coverage

| Test File | Test Classes | Scenarios | Coverage Area |
|-----------|-------------|-----------|---------------|
| test_match_queries.py | 7 | 25+ | Match search and filtering |
| test_team_queries.py | 8 | 30+ | Team statistics and performance |
| test_player_queries.py | 9 | 28+ | Player search and analysis |
| test_statistics.py | 10 | 32+ | Statistical calculations |
| **TOTAL** | **34** | **115+** | **Complete MCP functionality** |

---

## 1. Match Queries (test_match_queries.py)

### Test Class: TestFindMatchesBetweenTwoTeams

**Purpose**: Find matches between two specific teams

**Scenarios**:
1. Search for Flamengo vs Fluminense (Fla-Flu derby)
2. Search for Palmeiras vs Corinthians (Classic derby)
3. Search for Santos vs São Paulo (Handle special characters)

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I search for matches between 'Flamengo' and 'Fluminense'
Then I should receive a list of Fla-Flu derby matches
And each match should have dates, scores, and competition
```

### Test Class: TestFindMatchesByDateRange

**Purpose**: Filter matches by date range

**Scenarios**:
1. Search for matches in 2023 (full year)
2. Search for matches in May 2012 (specific month)
3. Search for matches from 2015-2016 (multi-year range)

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I search for matches from '2023-01-01' to '2023-12-31'
Then I should receive all matches from the 2023 season
And all match dates should be within the specified range
```

### Test Class: TestFindMatchesByCompetition

**Purpose**: Filter matches by competition

**Scenarios**:
1. Search for Brasileirão matches
2. Search for Copa do Brasil matches
3. Search for Copa Libertadores matches

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I search for 'Brasileirão' matches
Then I should receive only Brasileirão Serie A matches
And all matches should be labeled with correct competition
```

### Test Class: TestFindMatchesBySeason

**Purpose**: Filter matches by season/year

**Scenarios**:
1. Search for all matches from 2019
2. Search for matches from 2012 (earliest season)
3. Search for Flamengo matches in 2019

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I search for matches from season 2019
Then I should receive all matches from 2019
And each match should have season field set to 2019
```

### Test Class: TestFindDerbyMatches

**Purpose**: Find classic derby matches between rivals

**Scenarios**:
1. Fla-Flu: Flamengo vs Fluminense (Rio de Janeiro)
2. Clássico Paulista: Corinthians vs Palmeiras (São Paulo)
3. Grenal: Grêmio vs Internacional (Porto Alegre)
4. Choque-Rei: Palmeiras vs São Paulo

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I search for 'Fla-Flu' derby matches
Then I should receive Flamengo vs Fluminense matches
And matches should include head-to-head statistics
```

### Test Class: TestMatchQueryEdgeCases

**Purpose**: Handle edge cases in match queries

**Scenarios**:
1. Team name variations (Flamengo vs Flamengo-RJ)
2. Non-existent team search
3. Special characters in team names (São Paulo)

### Test Class: TestCombinedMatchFilters

**Purpose**: Combine multiple search criteria

**Scenarios**:
1. Palmeiras matches in Brasileirão 2019
2. Flamengo home matches in 2023

---

## 2. Team Queries (test_team_queries.py)

### Test Class: TestTeamHomeAwayRecord

**Purpose**: Analyze home vs away performance

**Scenarios**:
1. Corinthians home record for 2022
2. Flamengo away record for 2019
3. Palmeiras home and away comparison

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I request Corinthians' home record for 2022
Then I should receive home match statistics
And statistics should include wins, draws, losses, and win rate
```

### Test Class: TestTeamWinLossDrawStats

**Purpose**: Calculate comprehensive team records

**Scenarios**:
1. Palmeiras 2023 statistics
2. Santos all-time statistics
3. Fluminense Brasileirão-specific statistics

### Test Class: TestTeamGoalsStatistics

**Purpose**: Analyze goals scored and conceded

**Scenarios**:
1. Flamengo's 2019 goal statistics
2. Atlético Mineiro's goal averages
3. Find highest scoring team in 2023

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I request Flamengo's 2019 goal statistics
Then I should receive goals scored and conceded
And goal difference should be calculated correctly
```

### Test Class: TestCompareTeamPerformance

**Purpose**: Compare team performance across seasons

**Scenarios**:
1. Palmeiras 2018 vs 2019 comparison
2. Flamengo multi-season progression (2017-2020)
3. Corinthians best vs worst seasons

### Test Class: TestHeadToHeadComparison

**Purpose**: Direct team comparisons

**Scenarios**:
1. Flamengo vs Palmeiras all-time
2. Grêmio vs Internacional in 2023
3. São Paulo vs Santos (special characters)

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I compare Flamengo vs Palmeiras all-time
Then I should receive head-to-head statistics
And total matches should equal sum of wins and draws
```

### Test Class: TestTeamStreaksAndTrends

**Purpose**: Identify winning/losing streaks

**Scenarios**:
1. Flamengo's 2019 winning streak
2. Palmeiras' 2018 unbeaten run

### Test Class: TestTeamDefensiveRecords

**Purpose**: Analyze defensive performance

**Scenarios**:
1. Atlético-MG clean sheets in 2021
2. Santos goals conceded per match

### Test Class: TestTeamFormAnalysis

**Purpose**: Recent form analysis

**Scenarios**:
1. Flamengo's last 5 matches
2. Palmeiras' form in last 10 matches

---

## 3. Player Queries (test_player_queries.py)

### Test Class: TestSearchPlayerByName

**Purpose**: Search players by name

**Scenarios**:
1. Search for "Neymar" (exact match)
2. Search for "Gabriel" (partial match, multiple results)
3. Search for "Messi"

**Given-When-Then**:
```gherkin
Given the player data is loaded
When I search for 'Neymar'
Then I should find Neymar Jr's player record
And record should include nationality, club, position, rating
```

### Test Class: TestFilterPlayersByNationality

**Purpose**: Filter players by country

**Scenarios**:
1. Filter for Brazilian players
2. Filter for Argentine players
3. Filter for Portuguese players

**Given-When-Then**:
```gherkin
Given the player data is loaded
When I filter for Brazilian players
Then I should receive all Brazilian players
And all players should have nationality "Brazil"
```

### Test Class: TestFilterPlayersByClub

**Purpose**: Find players by club

**Scenarios**:
1. Filter for Flamengo players
2. Filter for Palmeiras players
3. Filter for FC Barcelona players
4. Filter for São Paulo FC (special characters)

### Test Class: TestGetTopRatedPlayers

**Purpose**: Get highest-rated players

**Scenarios**:
1. Top 10 players overall
2. Top 5 Brazilian players
3. Top 10 forwards
4. Top Brazilian players at Brazilian clubs

**Given-When-Then**:
```gherkin
Given the player data is loaded
When I request top 10 players overall
Then I should receive the 10 highest-rated players
And players should be sorted by rating descending
And top players should include Messi, Ronaldo, Neymar
```

### Test Class: TestPlayerAttributeQueries

**Purpose**: Access detailed player attributes

**Scenarios**:
1. Neymar's skill attributes
2. Goalkeeper-specific attributes (De Gea)

### Test Class: TestBrazilianPlayersAtBrazilianClubs

**Purpose**: Find domestic talent

**Scenarios**:
1. Brazilians at Flamengo
2. Brazilians at Palmeiras
3. All Brazilians at Brazilian clubs

### Test Class: TestPlayerPositionQueries

**Purpose**: Query by playing position

**Scenarios**:
1. Search for strikers (ST)
2. Search for goalkeepers (GK)
3. Search for wingers (LW/RW)

### Test Class: TestPlayerAgeAndPotential

**Purpose**: Filter by age and potential

**Scenarios**:
1. Young high-potential players (under 23, 85+ potential)
2. Experienced players (over 30)

### Test Class: TestPlayerSearchEdgeCases

**Purpose**: Handle search edge cases

**Scenarios**:
1. Non-existent player
2. Special characters in names
3. Case-insensitive search

---

## 4. Statistics (test_statistics.py)

### Test Class: TestCalculateLeagueStandings

**Purpose**: Calculate league tables

**Scenarios**:
1. 2019 Brasileirão standings (Flamengo champion)
2. 2018 Brasileirão standings (Palmeiras champion)
3. 2023 standings with complete statistics

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I calculate 2019 Brasileirão standings
Then I should receive the complete table with Flamengo as champion
And teams should be sorted by points then goal difference
And each team should have wins, draws, losses, goals
```

### Test Class: TestFindBiggestWins

**Purpose**: Identify largest victories

**Scenarios**:
1. Top 10 biggest wins overall
2. Biggest Brasileirão wins
3. Biggest wins in 2019

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I request top 10 biggest wins
Then I should receive matches sorted by goal difference
And each match should show the winning margin
And goal differences should be 4+ goals
```

### Test Class: TestCalculateAverages

**Purpose**: Statistical averages

**Scenarios**:
1. Average goals per match in Brasileirão
2. Average goals in 2019
3. Overall average across all competitions

### Test Class: TestHeadToHeadRecords

**Purpose**: Detailed head-to-head statistics

**Scenarios**:
1. Flamengo vs Fluminense complete record
2. Palmeiras vs Corinthians all-time
3. Grêmio vs Internacional in Brasileirão only

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I get Flamengo vs Fluminense head-to-head
Then I should receive complete derby statistics
And statistics should include wins, draws, goals for both teams
And total matches should equal sum of wins and draws
```

### Test Class: TestHomeAdvantageStatistics

**Purpose**: Quantify home field advantage

**Scenarios**:
1. Home advantage in Brasileirão
2. Home advantage in 2019
3. Compare home advantage across seasons

**Given-When-Then**:
```gherkin
Given the match data is loaded
When I calculate home advantage in Brasileirão
Then I should receive home win/draw/away percentages
And percentages should sum to 100%
And home win percentage should be higher than away
```

### Test Class: TestTopScorersStatistics

**Purpose**: Identify highest-scoring teams

**Scenarios**:
1. Top scorers in 2019 Brasileirão (Flamengo expected)
2. Top 5 scoring teams in 2023

### Test Class: TestRelegationZoneAnalysis

**Purpose**: Track bottom-table teams

**Scenarios**:
1. Relegation zone for 2019 (bottom 4)
2. Relegation candidates in 2020

### Test Class: TestSeasonComparisonStatistics

**Purpose**: Multi-season trends

**Scenarios**:
1. Goals per match across 2017-2020
2. Home win rates across seasons

### Test Class: TestGoalDifferenceAnalysis

**Purpose**: Goal difference rankings

**Scenarios**:
1. Best goal difference in 2019 (Flamengo expected)
2. Worst goal difference identification

### Test Class: TestMatchOutcomeDistribution

**Purpose**: Outcome distribution analysis

**Scenarios**:
1. Outcome distribution in Brasileirão
2. High-scoring match frequency (3+ goals)

---

## Key Testing Features

### 1. Data Normalization
- Team name variations (with/without state suffixes)
- Case-insensitive searches
- Special character handling (UTF-8)

### 2. Date Handling
- Multiple date formats (ISO, Brazilian, with time)
- Date range filtering
- Season/year filtering

### 3. Statistical Accuracy
- Correct points calculation (3 for win, 1 for draw)
- Goal difference calculations
- Percentage calculations
- Sorting by multiple criteria

### 4. Edge Cases
- Non-existent entities
- Empty result sets
- Invalid inputs
- Special characters

### 5. Classic Derbies
- Fla-Flu (Flamengo vs Fluminense)
- Clássico Paulista (Corinthians vs Palmeiras)
- Grenal (Grêmio vs Internacional)
- Choque-Rei (Palmeiras vs São Paulo)

---

## Test Execution

### Quick Start
```bash
# Make script executable
chmod +x tests/run_tests.sh

# Run all tests
./tests/run_tests.sh

# Run specific test suite
./tests/run_tests.sh match
./tests/run_tests.sh team
./tests/run_tests.sh player
./tests/run_tests.sh stats

# Run with coverage
./tests/run_tests.sh coverage
```

### Direct PyTest
```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_match_queries.py -v

# Specific class
pytest tests/test_match_queries.py::TestFindDerbyMatches -v

# With markers
pytest tests/ -m derby -v
```

---

## Expected Outcomes

### Success Metrics
- ✅ All 115+ scenarios pass
- ✅ < 2 seconds for simple lookups
- ✅ < 5 seconds for aggregate queries
- ✅ < 10 seconds for complex statistics
- ✅ Proper UTF-8 encoding
- ✅ Correct team name normalization
- ✅ Accurate calculations

### Data Coverage
- ✅ 4,180 Brasileirão matches
- ✅ 1,337 Copa do Brasil matches
- ✅ 1,255 Libertadores matches
- ✅ 18,207 FIFA players
- ✅ Multiple seasons (2003-2023)
- ✅ 20+ Brazilian clubs

---

## Test Philosophy

These tests embody the **Given-When-Then** BDD philosophy:

1. **Given**: Establish clear preconditions
2. **When**: Execute specific actions
3. **Then**: Assert expected outcomes

Each scenario is:
- **Independent**: Can run in any order
- **Repeatable**: Produces same results
- **Clear**: Easy to understand intent
- **Comprehensive**: Covers edge cases
- **Fast**: Executes quickly

---

## Future Enhancements

Potential additional scenarios:
- Player career statistics
- Manager/coach records
- Stadium-specific analysis
- Weather impact studies
- Referee statistics
- Time-of-day performance
- Fan attendance correlation
- Form-based predictions
- Derby intensity metrics
- Transfer market analysis

---

## Maintenance

When updating tests:
1. Follow existing GWT pattern
2. Add to appropriate test class
3. Update scenario count in this document
4. Run full test suite
5. Update TEST_SCENARIOS_README.md
6. Commit with descriptive message

---

## Credits

**Test Design**: Tester Agent (Hive Mind)
**Test Framework**: pytest with BDD-style parametrization
**Coverage**: Match, Team, Player, and Statistics queries
**Data Sources**: Kaggle Brazilian soccer datasets
**Philosophy**: Behavior-Driven Development (BDD)

---

**Last Updated**: 2025-12-15
**Version**: 1.0
**Status**: Complete and Ready for Implementation
