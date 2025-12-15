"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: data_loader.py
Description: Data loading and preprocessing for Brazilian Soccer MCP Server
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Load and preprocess all CSV datasets for the Brazilian soccer knowledge
    graph. This module handles:
    - Loading 6 Kaggle CSV files into pandas DataFrames
    - Normalizing team names across datasets
    - Parsing dates from multiple formats
    - Converting raw data to Pydantic models
    - Handling character encoding (UTF-8 for Portuguese)

Data Sources:
    1. Brasileirao_Matches.csv (4,180 matches) - Serie A matches 2012+
    2. Brazilian_Cup_Matches.csv (1,337 matches) - Copa do Brasil
    3. Libertadores_Matches.csv (1,255 matches) - Copa Libertadores
    4. BR-Football-Dataset.csv (10,296 matches) - Extended statistics
    5. novo_campeonato_brasileiro.csv (6,886 matches) - Historical 2003-2019
    6. fifa_data.csv (18,207 players) - FIFA player database

Column Mappings:
    Different datasets use different column names that need mapping:
    - home_team / Equipe_mandante / home
    - away_team / Equipe_visitante / away
    - home_goal / Gols_mandante / home_goal
    - datetime / Data / date
=============================================================================
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np

from .models import Match, Player, Competition, Team
from .utils import normalize_team_name, parse_date, safe_int, extract_state


class DataLoader:
    """
    Loads and manages all Brazilian soccer data from CSV files.

    Attributes:
        data_dir: Path to the data/kaggle directory
        matches: All matches from all competitions
        players: All FIFA player records
        teams: Set of all team names
        _dataframes: Raw pandas DataFrames for each file
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the data loader.

        Args:
            data_dir: Path to data directory. Defaults to data/kaggle relative
                     to project root.
        """
        if data_dir is None:
            # Find data directory relative to this file
            module_dir = Path(__file__).parent
            project_root = module_dir.parent.parent
            data_dir = project_root / "data" / "kaggle"

        self.data_dir = Path(data_dir)
        self.matches: List[Match] = []
        self.players: List[Player] = []
        self.teams: Dict[str, Team] = {}
        self._dataframes: Dict[str, pd.DataFrame] = {}
        self._loaded = False

    def load_all(self) -> None:
        """Load all data sources."""
        if self._loaded:
            return

        self._load_brasileirao_matches()
        self._load_copa_do_brasil_matches()
        self._load_libertadores_matches()
        self._load_extended_stats()
        self._load_historical_matches()
        self._load_fifa_players()
        self._build_teams_index()
        self._loaded = True

    def _read_csv(self, filename: str, encoding: str = "utf-8") -> Optional[pd.DataFrame]:
        """
        Read a CSV file with proper encoding handling.

        Args:
            filename: Name of the CSV file
            encoding: Character encoding to use

        Returns:
            DataFrame or None if file not found
        """
        filepath = self.data_dir / filename
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            return None

        try:
            # Try UTF-8 first, then Latin-1 as fallback
            try:
                df = pd.read_csv(filepath, encoding=encoding)
            except UnicodeDecodeError:
                df = pd.read_csv(filepath, encoding="latin-1")

            self._dataframes[filename] = df
            return df
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return None

    def _load_brasileirao_matches(self) -> None:
        """Load Brasileirao Serie A matches."""
        df = self._read_csv("Brasileirao_Matches.csv")
        if df is None:
            return

        for _, row in df.iterrows():
            match = Match(
                match_date=parse_date(str(row.get("datetime", ""))),
                home_team=normalize_team_name(str(row.get("home_team", ""))),
                away_team=normalize_team_name(str(row.get("away_team", ""))),
                home_team_state=row.get("home_team_state"),
                away_team_state=row.get("away_team_state"),
                home_goals=safe_int(row.get("home_goal")),
                away_goals=safe_int(row.get("away_goal")),
                season=safe_int(row.get("season")),
                match_round=safe_int(row.get("round")),
                competition=Competition.BRASILEIRAO,
            )
            self.matches.append(match)

    def _load_copa_do_brasil_matches(self) -> None:
        """Load Copa do Brasil matches."""
        df = self._read_csv("Brazilian_Cup_Matches.csv")
        if df is None:
            return

        for _, row in df.iterrows():
            match = Match(
                match_date=parse_date(str(row.get("datetime", ""))),
                home_team=normalize_team_name(str(row.get("home_team", ""))),
                away_team=normalize_team_name(str(row.get("away_team", ""))),
                home_goals=safe_int(row.get("home_goal")),
                away_goals=safe_int(row.get("away_goal")),
                season=safe_int(row.get("season")),
                stage=str(row.get("round", "")),
                competition=Competition.COPA_DO_BRASIL,
            )
            self.matches.append(match)

    def _load_libertadores_matches(self) -> None:
        """Load Copa Libertadores matches."""
        df = self._read_csv("Libertadores_Matches.csv")
        if df is None:
            return

        for _, row in df.iterrows():
            match = Match(
                match_date=parse_date(str(row.get("datetime", ""))),
                home_team=normalize_team_name(str(row.get("home_team", ""))),
                away_team=normalize_team_name(str(row.get("away_team", ""))),
                home_goals=safe_int(row.get("home_goal")),
                away_goals=safe_int(row.get("away_goal")),
                season=safe_int(row.get("season")),
                stage=str(row.get("stage", "")),
                competition=Competition.LIBERTADORES,
            )
            self.matches.append(match)

    def _load_extended_stats(self) -> None:
        """Load extended match statistics from BR-Football-Dataset."""
        df = self._read_csv("BR-Football-Dataset.csv")
        if df is None:
            return

        # This dataset has different column names
        for _, row in df.iterrows():
            date_str = str(row.get("date", ""))
            match = Match(
                match_date=parse_date(date_str),
                home_team=normalize_team_name(str(row.get("home", ""))),
                away_team=normalize_team_name(str(row.get("away", ""))),
                home_goals=safe_int(row.get("home_goal")),
                away_goals=safe_int(row.get("away_goal")),
                competition=Competition.UNKNOWN,  # Multiple competitions in this file
            )
            # Only add if not a duplicate
            if match.home_team and match.away_team:
                self.matches.append(match)

    def _load_historical_matches(self) -> None:
        """Load historical Brasileirao matches (2003-2019)."""
        df = self._read_csv("novo_campeonato_brasileiro.csv")
        if df is None:
            return

        # This dataset uses Portuguese column names
        for _, row in df.iterrows():
            match = Match(
                id=safe_int(row.get("ID")),
                match_date=parse_date(str(row.get("Data", ""))),
                home_team=normalize_team_name(str(row.get("Equipe_mandante", ""))),
                away_team=normalize_team_name(str(row.get("Equipe_visitante", ""))),
                home_team_state=row.get("Mandante_UF"),
                away_team_state=row.get("Visitante_UF"),
                home_goals=safe_int(row.get("Gols_mandante")),
                away_goals=safe_int(row.get("Gols_visitante")),
                season=safe_int(row.get("Ano")),
                match_round=safe_int(row.get("Rodada")),
                venue=str(row.get("Arena", "")) if pd.notna(row.get("Arena")) else None,
                competition=Competition.BRASILEIRAO,
            )
            self.matches.append(match)

    def _load_fifa_players(self) -> None:
        """Load FIFA player database."""
        df = self._read_csv("fifa_data.csv")
        if df is None:
            return

        # Skill columns to extract
        skill_columns = [
            "Crossing", "Finishing", "HeadingAccuracy", "ShortPassing",
            "Volleys", "Dribbling", "Curve", "FKAccuracy", "LongPassing",
            "BallControl", "Acceleration", "SprintSpeed", "Agility",
            "Reactions", "Balance", "ShotPower", "Jumping", "Stamina",
            "Strength", "LongShots", "Aggression", "Interceptions",
            "Positioning", "Vision", "Penalties", "Composure",
        ]

        for _, row in df.iterrows():
            # Extract skills
            skills = {}
            for skill in skill_columns:
                if skill in row and pd.notna(row[skill]):
                    skills[skill] = safe_int(row[skill])

            player = Player(
                id=safe_int(row.get("ID", 0)),
                name=str(row.get("Name", "")),
                age=safe_int(row.get("Age")),
                nationality=str(row.get("Nationality", "")) if pd.notna(row.get("Nationality")) else None,
                overall=safe_int(row.get("Overall")),
                potential=safe_int(row.get("Potential")),
                club=str(row.get("Club", "")) if pd.notna(row.get("Club")) else None,
                position=str(row.get("Position", "")) if pd.notna(row.get("Position")) else None,
                jersey_number=safe_int(row.get("Jersey Number")) if pd.notna(row.get("Jersey Number")) else None,
                height=str(row.get("Height", "")) if pd.notna(row.get("Height")) else None,
                weight=str(row.get("Weight", "")) if pd.notna(row.get("Weight")) else None,
                preferred_foot=str(row.get("Preferred Foot", "")) if pd.notna(row.get("Preferred Foot")) else None,
                skills=skills,
            )
            self.players.append(player)

    def _build_teams_index(self) -> None:
        """Build index of all teams from match data."""
        team_names = set()

        for match in self.matches:
            if match.home_team:
                team_names.add(match.home_team)
            if match.away_team:
                team_names.add(match.away_team)

        for name in team_names:
            self.teams[name.lower()] = Team(
                name=name,
                state=extract_state(name),
            )

    def get_matches(
        self,
        team: Optional[str] = None,
        opponent: Optional[str] = None,
        competition: Optional[Competition] = None,
        season: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Match]:
        """
        Filter matches by various criteria.

        Args:
            team: Team name (matches home or away)
            opponent: Opponent team name (requires team to be set)
            competition: Filter by competition
            season: Filter by season year
            start_date: Filter matches on or after this date
            end_date: Filter matches on or before this date

        Returns:
            List of matching Match objects
        """
        results = self.matches

        if team:
            team_lower = normalize_team_name(team).lower()
            results = [
                m for m in results
                if team_lower in m.home_team.lower() or team_lower in m.away_team.lower()
            ]

        if opponent and team:
            opponent_lower = normalize_team_name(opponent).lower()
            results = [
                m for m in results
                if opponent_lower in m.home_team.lower() or opponent_lower in m.away_team.lower()
            ]

        if competition:
            results = [m for m in results if m.competition == competition]

        if season:
            results = [m for m in results if m.season == season]

        if start_date:
            start_dt = parse_date(start_date)
            if start_dt:
                results = [m for m in results if m.match_date and m.match_date >= start_dt]

        if end_date:
            end_dt = parse_date(end_date)
            if end_dt:
                results = [m for m in results if m.match_date and m.match_date <= end_dt]

        # Sort by date (most recent first)
        results.sort(key=lambda m: m.match_date or pd.Timestamp.min, reverse=True)

        return results

    def get_players(
        self,
        name: Optional[str] = None,
        nationality: Optional[str] = None,
        club: Optional[str] = None,
        position: Optional[str] = None,
        min_overall: Optional[int] = None,
        max_overall: Optional[int] = None,
    ) -> List[Player]:
        """
        Filter players by various criteria.

        Args:
            name: Player name (partial match)
            nationality: Country name
            club: Club name (partial match)
            position: Playing position
            min_overall: Minimum FIFA overall rating
            max_overall: Maximum FIFA overall rating

        Returns:
            List of matching Player objects
        """
        results = self.players

        if name:
            name_lower = name.lower()
            results = [p for p in results if name_lower in p.name.lower()]

        if nationality:
            nat_lower = nationality.lower()
            results = [p for p in results if p.nationality and nat_lower in p.nationality.lower()]

        if club:
            club_lower = club.lower()
            results = [p for p in results if p.club and club_lower in p.club.lower()]

        if position:
            pos_upper = position.upper()
            results = [p for p in results if p.position and pos_upper in p.position.upper()]

        if min_overall is not None:
            results = [p for p in results if p.overall >= min_overall]

        if max_overall is not None:
            results = [p for p in results if p.overall <= max_overall]

        # Sort by overall rating (highest first)
        results.sort(key=lambda p: p.overall, reverse=True)

        return results

    def get_team_names(self) -> List[str]:
        """Get list of all team names."""
        return list(self.teams.keys())

    def get_seasons(self) -> List[int]:
        """Get list of all seasons in the data."""
        seasons = set()
        for match in self.matches:
            if match.season:
                seasons.add(match.season)
        return sorted(seasons, reverse=True)

    @property
    def total_matches(self) -> int:
        """Total number of matches loaded."""
        return len(self.matches)

    @property
    def total_players(self) -> int:
        """Total number of players loaded."""
        return len(self.players)

    @property
    def total_teams(self) -> int:
        """Total number of unique teams."""
        return len(self.teams)
