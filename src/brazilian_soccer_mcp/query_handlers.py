"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: query_handlers.py
Description: Query processing handlers for Brazilian Soccer MCP Server
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Implement query processing logic for all supported query types:
    - Match queries (by team, date, competition, season)
    - Team statistics (wins, losses, goals, records)
    - Player queries (by name, nationality, club, position)
    - Head-to-head comparisons
    - Statistical analysis (standings, averages, biggest wins)

Query Types:
    1. search_matches: Find matches by criteria
    2. get_team_stats: Calculate team statistics
    3. search_players: Find players by criteria
    4. get_head_to_head: Compare two teams
    5. get_standings: Calculate league standings
    6. get_statistics: General statistical queries

Response Formatting:
    All queries return standardized QueryResult objects with:
    - success: Boolean status
    - query_type: Type of query
    - count: Number of results
    - data: Query-specific results
    - message: Human-readable summary
=============================================================================
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from .models import (
    Match, Player, TeamStats, HeadToHead, QueryResult, Competition
)
from .data_loader import DataLoader
from .vector_store import VectorStore
from .utils import normalize_team_name, is_derby


class QueryHandler:
    """
    Handles all query types for the Brazilian Soccer MCP server.

    Combines structured data queries (via DataLoader) with semantic
    search (via VectorStore) to provide comprehensive query capabilities.

    Attributes:
        data_loader: DataLoader instance with CSV data
        vector_store: VectorStore for semantic search
    """

    def __init__(self, data_loader: DataLoader, vector_store: Optional[VectorStore] = None):
        """
        Initialize the query handler.

        Args:
            data_loader: DataLoader instance (must be loaded)
            vector_store: Optional VectorStore for semantic search
        """
        self.data_loader = data_loader
        self.vector_store = vector_store

    def search_matches(
        self,
        team: Optional[str] = None,
        opponent: Optional[str] = None,
        competition: Optional[str] = None,
        season: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> QueryResult:
        """
        Search for matches by criteria.

        Args:
            team: Team name (home or away)
            opponent: Opponent team (requires team to be set)
            competition: Competition name (brasileirao, copa_do_brasil, libertadores)
            season: Season year
            start_date: Start date filter (YYYY-MM-DD)
            end_date: End date filter (YYYY-MM-DD)
            limit: Maximum results to return

        Returns:
            QueryResult with matching matches
        """
        # Convert competition string to enum
        comp_enum = None
        if competition:
            comp_map = {
                "brasileirao": Competition.BRASILEIRAO,
                "copa_do_brasil": Competition.COPA_DO_BRASIL,
                "libertadores": Competition.LIBERTADORES,
            }
            comp_enum = comp_map.get(competition.lower())

        matches = self.data_loader.get_matches(
            team=team,
            opponent=opponent,
            competition=comp_enum,
            season=season,
            start_date=start_date,
            end_date=end_date,
        )[:limit]

        # Format matches for response
        match_data = []
        for m in matches:
            is_derby_match, derby_name = is_derby(m.home_team, m.away_team)
            match_info = {
                "date": m.match_date.strftime("%Y-%m-%d") if m.match_date else None,
                "home_team": m.home_team,
                "away_team": m.away_team,
                "score": f"{m.home_goals}-{m.away_goals}",
                "competition": m.competition.value if m.competition else None,
                "season": m.season,
                "round": m.match_round,
                "winner": m.winner,
                "is_derby": is_derby_match,
                "derby_name": derby_name,
            }
            match_data.append(match_info)

        # Build message
        parts = []
        if team and opponent:
            parts.append(f"{team} vs {opponent}")
        elif team:
            parts.append(f"matches for {team}")
        if competition:
            parts.append(f"in {competition}")
        if season:
            parts.append(f"season {season}")

        message = f"Found {len(matches)} " + " ".join(parts) if parts else f"Found {len(matches)} matches"

        return QueryResult(
            success=True,
            query_type="match_search",
            count=len(matches),
            data=match_data,
            message=message,
        )

    def get_team_stats(
        self,
        team: str,
        season: Optional[int] = None,
        competition: Optional[str] = None,
    ) -> QueryResult:
        """
        Calculate team statistics.

        Args:
            team: Team name
            season: Optional season filter
            competition: Optional competition filter

        Returns:
            QueryResult with team statistics
        """
        # Convert competition string to enum
        comp_enum = None
        if competition:
            comp_map = {
                "brasileirao": Competition.BRASILEIRAO,
                "copa_do_brasil": Competition.COPA_DO_BRASIL,
                "libertadores": Competition.LIBERTADORES,
            }
            comp_enum = comp_map.get(competition.lower())

        matches = self.data_loader.get_matches(
            team=team,
            competition=comp_enum,
            season=season,
        )

        if not matches:
            return QueryResult(
                success=True,
                query_type="team_stats",
                count=0,
                data=None,
                message=f"No matches found for {team}",
            )

        # Calculate statistics
        team_normalized = normalize_team_name(team).lower()
        stats = TeamStats(team=team, season=season, competition=comp_enum)

        for match in matches:
            is_home = team_normalized in match.home_team.lower()
            is_away = team_normalized in match.away_team.lower()

            if not (is_home or is_away):
                continue

            stats.matches_played += 1

            if is_home:
                # Home match
                stats.goals_for += match.home_goals
                stats.goals_against += match.away_goals
                stats.home_goals_for += match.home_goals
                stats.home_goals_against += match.away_goals

                if match.home_goals > match.away_goals:
                    stats.wins += 1
                    stats.home_wins += 1
                elif match.home_goals < match.away_goals:
                    stats.losses += 1
                    stats.home_losses += 1
                else:
                    stats.draws += 1
                    stats.home_draws += 1
            else:
                # Away match
                stats.goals_for += match.away_goals
                stats.goals_against += match.home_goals
                stats.away_goals_for += match.away_goals
                stats.away_goals_against += match.home_goals

                if match.away_goals > match.home_goals:
                    stats.wins += 1
                    stats.away_wins += 1
                elif match.away_goals < match.home_goals:
                    stats.losses += 1
                    stats.away_losses += 1
                else:
                    stats.draws += 1
                    stats.away_draws += 1

        stats_data = {
            "team": stats.team,
            "season": stats.season,
            "competition": stats.competition.value if stats.competition else None,
            "matches_played": stats.matches_played,
            "wins": stats.wins,
            "draws": stats.draws,
            "losses": stats.losses,
            "points": stats.points,
            "goals_for": stats.goals_for,
            "goals_against": stats.goals_against,
            "goal_difference": stats.goal_difference,
            "win_rate": round(stats.win_rate, 1),
            "home_record": f"{stats.home_wins}W-{stats.home_draws}D-{stats.home_losses}L",
            "away_record": f"{stats.away_wins}W-{stats.away_draws}D-{stats.away_losses}L",
            "home_win_rate": round(stats.home_win_rate, 1),
            "away_win_rate": round(stats.away_win_rate, 1),
        }

        message = stats.format_summary()

        return QueryResult(
            success=True,
            query_type="team_stats",
            count=1,
            data=stats_data,
            message=message,
        )

    def search_players(
        self,
        name: Optional[str] = None,
        nationality: Optional[str] = None,
        club: Optional[str] = None,
        position: Optional[str] = None,
        min_overall: Optional[int] = None,
        limit: int = 20,
    ) -> QueryResult:
        """
        Search for players by criteria.

        Args:
            name: Player name (partial match)
            nationality: Country name
            club: Club name (partial match)
            position: Playing position
            min_overall: Minimum FIFA overall rating
            limit: Maximum results

        Returns:
            QueryResult with matching players
        """
        players = self.data_loader.get_players(
            name=name,
            nationality=nationality,
            club=club,
            position=position,
            min_overall=min_overall,
        )[:limit]

        player_data = []
        for p in players:
            player_info = {
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "nationality": p.nationality,
                "overall": p.overall,
                "potential": p.potential,
                "club": p.club,
                "position": p.position,
                "preferred_foot": p.preferred_foot,
            }
            player_data.append(player_info)

        # Build message
        parts = []
        if name:
            parts.append(f"named '{name}'")
        if nationality:
            parts.append(f"from {nationality}")
        if club:
            parts.append(f"at {club}")
        if position:
            parts.append(f"playing {position}")
        if min_overall:
            parts.append(f"rated {min_overall}+")

        filter_desc = " ".join(parts) if parts else ""
        message = f"Found {len(players)} players {filter_desc}".strip()

        return QueryResult(
            success=True,
            query_type="player_search",
            count=len(players),
            data=player_data,
            message=message,
        )

    def get_head_to_head(
        self,
        team1: str,
        team2: str,
        competition: Optional[str] = None,
        limit: int = 20,
    ) -> QueryResult:
        """
        Get head-to-head statistics between two teams.

        Args:
            team1: First team name
            team2: Second team name
            competition: Optional competition filter
            limit: Maximum matches to include

        Returns:
            QueryResult with head-to-head statistics
        """
        # Get matches between the two teams
        result = self.search_matches(team=team1, opponent=team2, competition=competition, limit=limit)

        if result.count == 0:
            return QueryResult(
                success=True,
                query_type="head_to_head",
                count=0,
                data=None,
                message=f"No matches found between {team1} and {team2}",
            )

        # Calculate H2H stats
        team1_norm = normalize_team_name(team1).lower()
        team2_norm = normalize_team_name(team2).lower()

        h2h = HeadToHead(team1=team1, team2=team2)
        h2h.total_matches = result.count

        for match_data in result.data:
            home = match_data["home_team"].lower()
            away = match_data["away_team"].lower()
            score_parts = match_data["score"].split("-")
            home_goals = int(score_parts[0])
            away_goals = int(score_parts[1])

            # Determine which team is which
            team1_is_home = team1_norm in home
            team1_goals = home_goals if team1_is_home else away_goals
            team2_goals = away_goals if team1_is_home else home_goals

            h2h.team1_goals += team1_goals
            h2h.team2_goals += team2_goals

            if team1_goals > team2_goals:
                h2h.team1_wins += 1
            elif team2_goals > team1_goals:
                h2h.team2_wins += 1
            else:
                h2h.draws += 1

        # Check if it's a classic derby
        is_derby_match, derby_name = is_derby(team1, team2)

        h2h_data = {
            "team1": h2h.team1,
            "team2": h2h.team2,
            "total_matches": h2h.total_matches,
            "team1_wins": h2h.team1_wins,
            "team2_wins": h2h.team2_wins,
            "draws": h2h.draws,
            "team1_goals": h2h.team1_goals,
            "team2_goals": h2h.team2_goals,
            "is_classic_derby": is_derby_match,
            "derby_name": derby_name,
            "recent_matches": result.data[:10],
        }

        message = h2h.format_summary()
        if derby_name:
            message = f"{derby_name}\n{message}"

        return QueryResult(
            success=True,
            query_type="head_to_head",
            count=h2h.total_matches,
            data=h2h_data,
            message=message,
        )

    def get_standings(
        self,
        season: int,
        competition: str = "brasileirao",
    ) -> QueryResult:
        """
        Calculate league standings for a season.

        Args:
            season: Season year
            competition: Competition name

        Returns:
            QueryResult with standings table
        """
        comp_map = {
            "brasileirao": Competition.BRASILEIRAO,
            "copa_do_brasil": Competition.COPA_DO_BRASIL,
            "libertadores": Competition.LIBERTADORES,
        }
        comp_enum = comp_map.get(competition.lower(), Competition.BRASILEIRAO)

        matches = self.data_loader.get_matches(
            competition=comp_enum,
            season=season,
        )

        if not matches:
            return QueryResult(
                success=True,
                query_type="standings",
                count=0,
                data=None,
                message=f"No matches found for {competition} {season}",
            )

        # Calculate standings
        team_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            "matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "points": 0,
        })

        for match in matches:
            home = match.home_team
            away = match.away_team

            team_stats[home]["matches"] += 1
            team_stats[away]["matches"] += 1
            team_stats[home]["goals_for"] += match.home_goals
            team_stats[home]["goals_against"] += match.away_goals
            team_stats[away]["goals_for"] += match.away_goals
            team_stats[away]["goals_against"] += match.home_goals

            if match.home_goals > match.away_goals:
                team_stats[home]["wins"] += 1
                team_stats[home]["points"] += 3
                team_stats[away]["losses"] += 1
            elif match.away_goals > match.home_goals:
                team_stats[away]["wins"] += 1
                team_stats[away]["points"] += 3
                team_stats[home]["losses"] += 1
            else:
                team_stats[home]["draws"] += 1
                team_stats[away]["draws"] += 1
                team_stats[home]["points"] += 1
                team_stats[away]["points"] += 1

        # Sort by points, then goal difference
        standings = []
        for team, stats in team_stats.items():
            gd = stats["goals_for"] - stats["goals_against"]
            standings.append({
                "team": team,
                "matches": stats["matches"],
                "wins": stats["wins"],
                "draws": stats["draws"],
                "losses": stats["losses"],
                "goals_for": stats["goals_for"],
                "goals_against": stats["goals_against"],
                "goal_difference": gd,
                "points": stats["points"],
            })

        standings.sort(key=lambda x: (x["points"], x["goal_difference"], x["goals_for"]), reverse=True)

        # Add position
        for i, entry in enumerate(standings):
            entry["position"] = i + 1

        message_lines = [f"{competition.upper()} {season} Standings:"]
        for entry in standings[:5]:
            message_lines.append(
                f"{entry['position']}. {entry['team']} - {entry['points']} pts "
                f"({entry['wins']}W-{entry['draws']}D-{entry['losses']}L)"
            )

        return QueryResult(
            success=True,
            query_type="standings",
            count=len(standings),
            data=standings,
            message="\n".join(message_lines),
        )

    def get_statistics(
        self,
        stat_type: str,
        season: Optional[int] = None,
        competition: Optional[str] = None,
        limit: int = 10,
    ) -> QueryResult:
        """
        Get various statistical analyses.

        Args:
            stat_type: Type of statistic:
                - "biggest_wins": Matches with largest goal difference
                - "highest_scoring": Matches with most total goals
                - "avg_goals": Average goals per match
                - "best_home": Teams with best home record
                - "best_away": Teams with best away record
            season: Optional season filter
            competition: Optional competition filter
            limit: Maximum results

        Returns:
            QueryResult with statistics
        """
        comp_enum = None
        if competition:
            comp_map = {
                "brasileirao": Competition.BRASILEIRAO,
                "copa_do_brasil": Competition.COPA_DO_BRASIL,
                "libertadores": Competition.LIBERTADORES,
            }
            comp_enum = comp_map.get(competition.lower())

        matches = self.data_loader.get_matches(
            competition=comp_enum,
            season=season,
        )

        if not matches:
            return QueryResult(
                success=True,
                query_type=f"statistics_{stat_type}",
                count=0,
                data=None,
                message="No matches found for the given criteria",
            )

        if stat_type == "biggest_wins":
            # Sort by goal difference
            sorted_matches = sorted(
                matches,
                key=lambda m: abs(m.home_goals - m.away_goals),
                reverse=True
            )[:limit]

            data = []
            for m in sorted_matches:
                gd = abs(m.home_goals - m.away_goals)
                winner = m.home_team if m.home_goals > m.away_goals else m.away_team
                loser = m.away_team if m.home_goals > m.away_goals else m.home_team
                data.append({
                    "date": m.match_date.strftime("%Y-%m-%d") if m.match_date else None,
                    "match": f"{m.home_team} {m.home_goals}-{m.away_goals} {m.away_team}",
                    "winner": winner,
                    "loser": loser,
                    "goal_difference": gd,
                    "competition": m.competition.value if m.competition else None,
                })

            message = f"Biggest wins (top {len(data)}):\n"
            for i, d in enumerate(data[:5], 1):
                message += f"{i}. {d['match']} (GD: {d['goal_difference']})\n"

            return QueryResult(
                success=True,
                query_type="statistics_biggest_wins",
                count=len(data),
                data=data,
                message=message,
            )

        elif stat_type == "highest_scoring":
            # Sort by total goals
            sorted_matches = sorted(
                matches,
                key=lambda m: m.total_goals,
                reverse=True
            )[:limit]

            data = []
            for m in sorted_matches:
                data.append({
                    "date": m.match_date.strftime("%Y-%m-%d") if m.match_date else None,
                    "match": f"{m.home_team} {m.home_goals}-{m.away_goals} {m.away_team}",
                    "total_goals": m.total_goals,
                    "competition": m.competition.value if m.competition else None,
                })

            message = f"Highest scoring matches (top {len(data)}):\n"
            for i, d in enumerate(data[:5], 1):
                message += f"{i}. {d['match']} ({d['total_goals']} goals)\n"

            return QueryResult(
                success=True,
                query_type="statistics_highest_scoring",
                count=len(data),
                data=data,
                message=message,
            )

        elif stat_type == "avg_goals":
            total_goals = sum(m.total_goals for m in matches)
            avg = total_goals / len(matches) if matches else 0

            home_goals = sum(m.home_goals for m in matches)
            away_goals = sum(m.away_goals for m in matches)

            data = {
                "total_matches": len(matches),
                "total_goals": total_goals,
                "average_goals_per_match": round(avg, 2),
                "average_home_goals": round(home_goals / len(matches), 2) if matches else 0,
                "average_away_goals": round(away_goals / len(matches), 2) if matches else 0,
                "home_wins": sum(1 for m in matches if m.home_goals > m.away_goals),
                "away_wins": sum(1 for m in matches if m.away_goals > m.home_goals),
                "draws": sum(1 for m in matches if m.is_draw),
            }

            message = (
                f"Match Statistics ({len(matches)} matches):\n"
                f"Average goals per match: {data['average_goals_per_match']}\n"
                f"Home win rate: {data['home_wins']/len(matches)*100:.1f}%\n"
                f"Away win rate: {data['away_wins']/len(matches)*100:.1f}%\n"
                f"Draw rate: {data['draws']/len(matches)*100:.1f}%"
            )

            return QueryResult(
                success=True,
                query_type="statistics_avg_goals",
                count=1,
                data=data,
                message=message,
            )

        else:
            return QueryResult(
                success=False,
                query_type=f"statistics_{stat_type}",
                count=0,
                data=None,
                error=f"Unknown statistic type: {stat_type}",
            )

    def semantic_search(
        self,
        query: str,
        search_type: str = "all",
        limit: int = 10,
    ) -> QueryResult:
        """
        Perform semantic search using vector similarity.

        Args:
            query: Natural language query
            search_type: "matches", "players", or "all"
            limit: Maximum results

        Returns:
            QueryResult with semantically similar results
        """
        if not self.vector_store:
            return QueryResult(
                success=False,
                query_type="semantic_search",
                count=0,
                data=None,
                error="Vector store not initialized",
            )

        results = []

        if search_type in ("matches", "all"):
            match_results = self.vector_store.search_matches(query, k=limit)
            results.extend([{"type": "match", **r} for r in match_results])

        if search_type in ("players", "all"):
            player_results = self.vector_store.search_players(query, k=limit)
            results.extend([{"type": "player", **r} for r in player_results])

        return QueryResult(
            success=True,
            query_type="semantic_search",
            count=len(results),
            data=results[:limit],
            message=f"Found {len(results)} results for '{query}'",
        )
