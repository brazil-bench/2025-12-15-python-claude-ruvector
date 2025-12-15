"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: models.py
Description: Pydantic data models for Brazilian Soccer MCP Server
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Define strongly-typed data models for all soccer entities used in the
    MCP server. These models ensure data consistency, validation, and
    serialization across the application.

Models:
    - Match: Represents a single match with teams, scores, date, competition
    - Team: Represents a team with normalized name and state
    - Player: Represents a FIFA player with attributes and ratings
    - Competition: Enum of supported competitions
    - TeamStats: Aggregated team statistics (wins, losses, draws, goals)
    - HeadToHead: Head-to-head comparison between two teams
    - QueryResult: Standardized query response wrapper

Data Normalization:
    Team names are normalized to handle variations like:
    - "Palmeiras-SP" -> "Palmeiras"
    - "Sport Club Corinthians Paulista" -> "Corinthians"
    - "Flamengo-RJ" -> "Flamengo"
=============================================================================
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


class Competition(str, Enum):
    """Supported competitions in the dataset."""
    BRASILEIRAO = "brasileirao"
    COPA_DO_BRASIL = "copa_do_brasil"
    LIBERTADORES = "libertadores"
    UNKNOWN = "unknown"


class Team(BaseModel):
    """
    Represents a Brazilian soccer team.

    Attributes:
        name: Normalized team name (e.g., "Palmeiras")
        full_name: Full official name if available
        state: Brazilian state abbreviation (e.g., "SP", "RJ")
        aliases: Alternative names used in datasets
    """
    name: str
    full_name: Optional[str] = None
    state: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Remove state suffix and normalize team name."""
        if not v:
            return v
        # Remove state suffix like "-SP", "-RJ"
        if "-" in v and len(v.split("-")[-1]) == 2:
            parts = v.rsplit("-", 1)
            return parts[0].strip()
        return v.strip()


class Player(BaseModel):
    """
    Represents a FIFA player record.

    Attributes:
        id: Unique player identifier
        name: Player name
        age: Player age
        nationality: Country of origin
        overall: FIFA overall rating (0-99)
        potential: FIFA potential rating (0-99)
        club: Current club name
        position: Playing position (GK, CB, CM, ST, etc.)
        jersey_number: Shirt number
        height: Height in format like "5'11"
        weight: Weight in format like "165lbs"
        preferred_foot: Left or Right
        skills: Dictionary of skill ratings
    """
    id: int
    name: str
    age: Optional[int] = None
    nationality: Optional[str] = None
    overall: int = 0
    potential: int = 0
    club: Optional[str] = None
    position: Optional[str] = None
    jersey_number: Optional[int] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    preferred_foot: Optional[str] = None
    skills: Dict[str, int] = Field(default_factory=dict)

    def is_brazilian(self) -> bool:
        """Check if player is Brazilian."""
        return self.nationality and self.nationality.lower() == "brazil"

    def plays_for_brazilian_club(self) -> bool:
        """Check if player plays for a Brazilian club."""
        brazilian_clubs = [
            "flamengo", "palmeiras", "corinthians", "santos", "sao paulo",
            "gremio", "internacional", "cruzeiro", "atletico mineiro",
            "fluminense", "botafogo", "vasco", "bahia", "sport", "fortaleza"
        ]
        if not self.club:
            return False
        club_lower = self.club.lower()
        return any(bc in club_lower for bc in brazilian_clubs)


class Match(BaseModel):
    """
    Represents a single soccer match.

    Attributes:
        id: Unique match identifier (optional)
        match_date: Match date and time
        home_team: Home team name (normalized)
        away_team: Away team name (normalized)
        home_team_state: Home team state abbreviation
        away_team_state: Away team state abbreviation
        home_goals: Goals scored by home team
        away_goals: Goals scored by away team
        season: Year/season of the match
        match_round: Match round number (for league matches)
        stage: Tournament stage (for cup matches)
        competition: Which competition this match belongs to
        venue: Stadium name (if available)
    """
    id: Optional[int] = None
    match_date: Optional[datetime] = None
    home_team: str
    away_team: str
    home_team_state: Optional[str] = None
    away_team_state: Optional[str] = None
    home_goals: int = 0
    away_goals: int = 0
    season: Optional[int] = None
    match_round: Optional[int] = None
    stage: Optional[str] = None
    competition: Competition = Competition.UNKNOWN
    venue: Optional[str] = None

    @property
    def winner(self) -> Optional[str]:
        """Return the winning team name or None for a draw."""
        if self.home_goals > self.away_goals:
            return self.home_team
        elif self.away_goals > self.home_goals:
            return self.away_team
        return None

    @property
    def is_draw(self) -> bool:
        """Check if match ended in a draw."""
        return self.home_goals == self.away_goals

    @property
    def total_goals(self) -> int:
        """Total goals scored in the match."""
        return self.home_goals + self.away_goals

    def involves_team(self, team: str) -> bool:
        """Check if a team played in this match."""
        team_lower = team.lower()
        return (
            team_lower in self.home_team.lower() or
            team_lower in self.away_team.lower()
        )

    def get_team_result(self, team: str) -> Optional[str]:
        """Get result for a specific team: 'win', 'loss', or 'draw'."""
        team_lower = team.lower()
        is_home = team_lower in self.home_team.lower()
        is_away = team_lower in self.away_team.lower()

        if not (is_home or is_away):
            return None

        if self.is_draw:
            return "draw"

        if is_home:
            return "win" if self.home_goals > self.away_goals else "loss"
        else:
            return "win" if self.away_goals > self.home_goals else "loss"

    def format_result(self) -> str:
        """Format match result as string."""
        date_str = self.match_date.strftime("%Y-%m-%d") if self.match_date else "Unknown date"
        return f"{date_str}: {self.home_team} {self.home_goals}-{self.away_goals} {self.away_team}"


class TeamStats(BaseModel):
    """
    Aggregated statistics for a team.

    Attributes:
        team: Team name
        season: Season year (optional)
        competition: Competition (optional)
        matches_played: Total matches
        wins: Number of wins
        draws: Number of draws
        losses: Number of losses
        goals_for: Goals scored
        goals_against: Goals conceded
        home_wins/draws/losses: Home record breakdown
        away_wins/draws/losses: Away record breakdown
    """
    team: str
    season: Optional[int] = None
    competition: Optional[Competition] = None
    matches_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    home_wins: int = 0
    home_draws: int = 0
    home_losses: int = 0
    home_goals_for: int = 0
    home_goals_against: int = 0
    away_wins: int = 0
    away_draws: int = 0
    away_losses: int = 0
    away_goals_for: int = 0
    away_goals_against: int = 0

    @property
    def points(self) -> int:
        """Calculate points (3 for win, 1 for draw)."""
        return (self.wins * 3) + self.draws

    @property
    def goal_difference(self) -> int:
        """Calculate goal difference."""
        return self.goals_for - self.goals_against

    @property
    def win_rate(self) -> float:
        """Calculate win percentage."""
        if self.matches_played == 0:
            return 0.0
        return (self.wins / self.matches_played) * 100

    @property
    def home_win_rate(self) -> float:
        """Calculate home win percentage."""
        home_matches = self.home_wins + self.home_draws + self.home_losses
        if home_matches == 0:
            return 0.0
        return (self.home_wins / home_matches) * 100

    @property
    def away_win_rate(self) -> float:
        """Calculate away win percentage."""
        away_matches = self.away_wins + self.away_draws + self.away_losses
        if away_matches == 0:
            return 0.0
        return (self.away_wins / away_matches) * 100

    def format_summary(self) -> str:
        """Format stats as readable summary."""
        lines = [
            f"Team: {self.team}",
            f"Matches: {self.matches_played}",
            f"Record: {self.wins}W - {self.draws}D - {self.losses}L",
            f"Points: {self.points}",
            f"Goals: {self.goals_for} scored, {self.goals_against} conceded (GD: {self.goal_difference:+d})",
            f"Win Rate: {self.win_rate:.1f}%",
        ]
        if self.season:
            lines.insert(1, f"Season: {self.season}")
        if self.competition:
            lines.insert(2, f"Competition: {self.competition.value}")
        return "\n".join(lines)


class HeadToHead(BaseModel):
    """
    Head-to-head statistics between two teams.

    Attributes:
        team1: First team name
        team2: Second team name
        total_matches: Total matches played
        team1_wins: Wins by team1
        team2_wins: Wins by team2
        draws: Number of draws
        team1_goals: Total goals by team1
        team2_goals: Total goals by team2
        matches: List of individual matches
    """
    team1: str
    team2: str
    total_matches: int = 0
    team1_wins: int = 0
    team2_wins: int = 0
    draws: int = 0
    team1_goals: int = 0
    team2_goals: int = 0
    matches: List[Match] = Field(default_factory=list)

    def format_summary(self) -> str:
        """Format head-to-head as readable summary."""
        return (
            f"{self.team1} vs {self.team2}\n"
            f"Total Matches: {self.total_matches}\n"
            f"{self.team1} Wins: {self.team1_wins}\n"
            f"{self.team2} Wins: {self.team2_wins}\n"
            f"Draws: {self.draws}\n"
            f"Goals: {self.team1} {self.team1_goals} - {self.team2_goals} {self.team2}"
        )


class QueryResult(BaseModel):
    """
    Standardized wrapper for query results.

    Attributes:
        success: Whether query executed successfully
        query_type: Type of query performed
        count: Number of results
        data: Query results (matches, players, stats, etc.)
        message: Human-readable summary
        error: Error message if failed
    """
    success: bool = True
    query_type: str
    count: int = 0
    data: Any = None
    message: str = ""
    error: Optional[str] = None

    def to_response(self) -> Dict[str, Any]:
        """Convert to MCP response format."""
        if not self.success:
            return {"error": self.error, "success": False}
        return {
            "success": True,
            "query_type": self.query_type,
            "count": self.count,
            "message": self.message,
            "data": self.data,
        }
