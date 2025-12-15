"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: utils.py
Description: Utility functions for Brazilian Soccer MCP Server
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Provide common utility functions for data processing including:
    - Team name normalization (handle variations in dataset naming)
    - Date parsing (handle multiple date formats in datasets)
    - Text normalization for search queries
    - Brazilian diacritics handling (São, Grêmio, Avaí, etc.)

Key Functions:
    - normalize_team_name: Standardize team names across datasets
    - parse_date: Parse dates from multiple formats
    - remove_diacritics: Convert accented characters for search
    - fuzzy_match: Find similar team names for flexible queries
    - extract_state: Extract state abbreviation from team name

Team Name Mappings:
    The datasets use various naming conventions that must be normalized:
    - "Palmeiras-SP" -> "Palmeiras"
    - "Sport Club Corinthians Paulista" -> "Corinthians"
    - "CR Flamengo" -> "Flamengo"
    - "SE Palmeiras" -> "Palmeiras"
=============================================================================
"""

import re
import unicodedata
from datetime import datetime
from typing import Optional, Tuple, List
from dateutil import parser as date_parser


# Team name normalization mappings
TEAM_ALIASES = {
    # Full names to short names
    "sport club corinthians paulista": "corinthians",
    "sociedade esportiva palmeiras": "palmeiras",
    "clube de regatas do flamengo": "flamengo",
    "fluminense football club": "fluminense",
    "santos futebol clube": "santos",
    "sao paulo futebol clube": "sao paulo",
    "sao paulo fc": "sao paulo",
    "gremio foot-ball porto alegrense": "gremio",
    "sport club internacional": "internacional",
    "cruzeiro esporte clube": "cruzeiro",
    "clube atletico mineiro": "atletico mineiro",
    "atletico mg": "atletico mineiro",
    "atletico-mg": "atletico mineiro",
    "atletico pr": "athletico paranaense",
    "atletico-pr": "athletico paranaense",
    "athletico-pr": "athletico paranaense",
    "botafogo de futebol e regatas": "botafogo",
    "club de regatas vasco da gama": "vasco da gama",
    "vasco": "vasco da gama",
    "esporte clube bahia": "bahia",
    "sport club do recife": "sport",
    "sport recife": "sport",
    "fortaleza esporte clube": "fortaleza",
    "ceara sporting club": "ceara",
    "coritiba foot ball club": "coritiba",
    "goias esporte clube": "goias",
    "america futebol clube": "america mineiro",
    "america mg": "america mineiro",
    "america-mg": "america mineiro",
    "red bull bragantino": "bragantino",
    "rb bragantino": "bragantino",
    "cuiaba esporte clube": "cuiaba",
    "associacao chapecoense de futebol": "chapecoense",

    # Common variations with state suffix
    "palmeiras sp": "palmeiras",
    "flamengo rj": "flamengo",
    "corinthians sp": "corinthians",
    "santos sp": "santos",
    "sao paulo sp": "sao paulo",
    "gremio rs": "gremio",
    "internacional rs": "internacional",
    "cruzeiro mg": "cruzeiro",
    "fluminense rj": "fluminense",
    "botafogo rj": "botafogo",
    "vasco da gama rj": "vasco da gama",
}

# State abbreviations mapping
STATE_NAMES = {
    "SP": "São Paulo",
    "RJ": "Rio de Janeiro",
    "MG": "Minas Gerais",
    "RS": "Rio Grande do Sul",
    "PR": "Paraná",
    "SC": "Santa Catarina",
    "BA": "Bahia",
    "PE": "Pernambuco",
    "CE": "Ceará",
    "GO": "Goiás",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "PA": "Pará",
    "AM": "Amazonas",
    "RN": "Rio Grande do Norte",
    "PB": "Paraíba",
    "AL": "Alagoas",
    "SE": "Sergipe",
    "ES": "Espírito Santo",
    "DF": "Distrito Federal",
}

# Classic derbies/rivalries
CLASSIC_DERBIES = {
    ("flamengo", "fluminense"): "Fla-Flu",
    ("flamengo", "vasco da gama"): "Clássico dos Milhões",
    ("corinthians", "palmeiras"): "Derby Paulista",
    ("corinthians", "sao paulo"): "Majestoso",
    ("palmeiras", "sao paulo"): "Choque-Rei",
    ("santos", "corinthians"): "Clássico Alvinegro",
    ("gremio", "internacional"): "Gre-Nal",
    ("cruzeiro", "atletico mineiro"): "Clássico Mineiro",
    ("botafogo", "flamengo"): "Clássico da Rivalidade",
    ("bahia", "vitoria"): "Ba-Vi",
    ("sport", "nautico"): "Clássico dos Clássicos",
    ("fortaleza", "ceara"): "Clássico-Rei",
}


def remove_diacritics(text: str) -> str:
    """
    Remove diacritics/accents from text for normalized comparison.

    Args:
        text: Input text with possible accents

    Returns:
        Text with accents removed (e.g., "São Paulo" -> "Sao Paulo")
    """
    if not text:
        return text
    # Normalize to decomposed form (separate base char from diacritics)
    normalized = unicodedata.normalize("NFD", text)
    # Remove diacritic marks
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def normalize_team_name(name: str) -> str:
    """
    Normalize a team name for consistent matching across datasets.

    Handles:
    - State suffixes (e.g., "Palmeiras-SP" -> "Palmeiras")
    - Full official names (e.g., "Sport Club Corinthians Paulista" -> "Corinthians")
    - Accent normalization
    - Case normalization

    Args:
        name: Raw team name from dataset

    Returns:
        Normalized team name
    """
    if not name:
        return ""

    # Basic cleaning
    cleaned = name.strip()

    # Remove state suffix pattern (e.g., "-SP", "-RJ")
    state_suffix_pattern = r"-([A-Z]{2})$"
    match = re.search(state_suffix_pattern, cleaned)
    if match:
        cleaned = cleaned[: match.start()]

    # Normalize for lookup
    lookup_key = remove_diacritics(cleaned.lower())

    # Check aliases
    if lookup_key in TEAM_ALIASES:
        return TEAM_ALIASES[lookup_key].title()

    # Also check with spaces instead of hyphens
    lookup_key_spaces = lookup_key.replace("-", " ")
    if lookup_key_spaces in TEAM_ALIASES:
        return TEAM_ALIASES[lookup_key_spaces].title()

    # Return cleaned version with proper casing
    return cleaned.strip()


def extract_state(team_name: str) -> Optional[str]:
    """
    Extract state abbreviation from team name if present.

    Args:
        team_name: Team name possibly containing state suffix

    Returns:
        State abbreviation (e.g., "SP") or None
    """
    if not team_name:
        return None

    # Check for suffix pattern
    match = re.search(r"-([A-Z]{2})$", team_name)
    if match:
        state = match.group(1)
        if state in STATE_NAMES:
            return state

    return None


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date from various formats used in the datasets.

    Supported formats:
    - ISO: "2023-09-24"
    - Brazilian: "29/03/2003"
    - With time: "2012-05-19 18:30:00"
    - Various other formats handled by dateutil

    Args:
        date_str: Date string in any format

    Returns:
        Parsed datetime or None if parsing fails
    """
    if not date_str or date_str in ("", "NaN", "nan", "None", "null"):
        return None

    try:
        # Try dateutil parser which handles many formats
        return date_parser.parse(date_str, dayfirst=True)
    except (ValueError, TypeError):
        pass

    # Try specific formats as fallback
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def fuzzy_match_team(query: str, team_names: List[str], threshold: float = 0.6) -> List[str]:
    """
    Find team names that fuzzy match a query string.

    Args:
        query: Search query
        team_names: List of team names to search
        threshold: Minimum similarity score (0-1)

    Returns:
        List of matching team names
    """
    query_normalized = remove_diacritics(query.lower())
    matches = []

    for name in team_names:
        name_normalized = remove_diacritics(name.lower())

        # Exact substring match
        if query_normalized in name_normalized or name_normalized in query_normalized:
            matches.append(name)
            continue

        # Simple word-based matching
        query_words = set(query_normalized.split())
        name_words = set(name_normalized.split())

        if query_words & name_words:  # Any common words
            matches.append(name)

    return matches


def is_derby(team1: str, team2: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a match between two teams is a classic derby.

    Args:
        team1: First team name
        team2: Second team name

    Returns:
        Tuple of (is_derby, derby_name)
    """
    t1 = normalize_team_name(team1).lower()
    t2 = normalize_team_name(team2).lower()

    # Check both orderings
    for (a, b), name in CLASSIC_DERBIES.items():
        if (t1 == a and t2 == b) or (t1 == b and t2 == a):
            return True, name

    return False, None


def get_season_from_date(dt: datetime) -> int:
    """
    Determine the season year from a match date.

    Brazilian season typically runs from April to December.

    Args:
        dt: Match datetime

    Returns:
        Season year
    """
    return dt.year


def format_goals(home_goals: int, away_goals: int) -> str:
    """Format score as standard string."""
    return f"{home_goals}-{away_goals}"


def calculate_points(wins: int, draws: int) -> int:
    """Calculate league points (3 for win, 1 for draw)."""
    return (wins * 3) + draws


def safe_int(value, default: int = 0) -> int:
    """Safely convert a value to int."""
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
