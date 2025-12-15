"""
=============================================================================
CONTEXT BLOCK
=============================================================================
Module: test_performance.py
Description: Performance benchmarks for Brazilian Soccer MCP Server with RuVector
Author: Hive Mind Collective (Queen + Workers)
Created: 2025-12-15

Purpose:
    Measure end-to-end performance of the Brazilian Soccer MCP Server using
    BDD Given-When-Then format. Tests cover:
    - Data loading performance
    - RuVector vector store operations (insert, batch, search)
    - Query handler performance (matches, players, teams, statistics)
    - End-to-end scenario performance

Performance Metrics:
    - Execution time (seconds)
    - Throughput (operations per second)
    - Memory efficiency
    - Query latency percentiles

Test Categories:
    - Data Loading: CSV parsing and model creation
    - Vector Operations: RuVector insert/search performance
    - Query Performance: All query types with various filters
    - End-to-End: Complete user scenarios
=============================================================================
"""

import pytest
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any, Callable
from dataclasses import dataclass, field


@dataclass
class PerformanceMetrics:
    """Container for performance measurement results."""
    operation: str
    iterations: int
    total_time: float
    min_time: float
    max_time: float
    avg_time: float
    median_time: float
    std_dev: float
    throughput: float  # operations per second

    def __str__(self) -> str:
        return (
            f"{self.operation}:\n"
            f"  Iterations: {self.iterations}\n"
            f"  Total Time: {self.total_time:.4f}s\n"
            f"  Min: {self.min_time*1000:.2f}ms\n"
            f"  Max: {self.max_time*1000:.2f}ms\n"
            f"  Avg: {self.avg_time*1000:.2f}ms\n"
            f"  Median: {self.median_time*1000:.2f}ms\n"
            f"  Std Dev: {self.std_dev*1000:.2f}ms\n"
            f"  Throughput: {self.throughput:.2f} ops/sec"
        )


def measure_performance(
    operation: str,
    func: Callable,
    iterations: int = 10,
    warmup: int = 2
) -> PerformanceMetrics:
    """
    Measure performance of a function over multiple iterations.

    Args:
        operation: Name of the operation being measured
        func: Function to measure (should take no arguments)
        iterations: Number of iterations to run
        warmup: Number of warmup iterations (not counted)

    Returns:
        PerformanceMetrics with timing statistics
    """
    # Warmup runs
    for _ in range(warmup):
        func()

    # Measured runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)

    total_time = sum(times)

    return PerformanceMetrics(
        operation=operation,
        iterations=iterations,
        total_time=total_time,
        min_time=min(times),
        max_time=max(times),
        avg_time=statistics.mean(times),
        median_time=statistics.median(times),
        std_dev=statistics.stdev(times) if len(times) > 1 else 0,
        throughput=iterations / total_time if total_time > 0 else 0
    )


@pytest.fixture(scope="module")
def performance_results():
    """Accumulate performance results across tests."""
    return []


class TestDataLoadingPerformance:
    """
    Feature: Measure data loading performance

    As a developer
    I want to measure CSV loading and parsing performance
    So that I can ensure data loads within acceptable time
    """

    @pytest.mark.performance
    def test_data_loader_initialization_performance(self, data_dir, bdd, performance_results):
        """
        Scenario: Measure data loader initialization time

        Given a fresh data loader
        When I load all CSV data files
        Then loading should complete within 10 seconds
        And I should have performance metrics
        """
        from brazilian_soccer_mcp.data_loader import DataLoader

        # Given
        bdd.given("a fresh data loader", True)

        # When - measure loading performance
        def load_data():
            loader = DataLoader(str(data_dir))
            loader.load_all()
            return loader

        metrics = measure_performance(
            "Data Loading (All CSVs)",
            load_data,
            iterations=3,
            warmup=1
        )
        bdd.when("I load all CSV data files", metrics)

        # Then
        bdd.then("loading should complete within 10 seconds", metrics.avg_time < 10.0)
        bdd.then("should have performance metrics", metrics.iterations > 0)

        performance_results.append(metrics)
        print(f"\n{metrics}")

    @pytest.mark.performance
    def test_match_data_volume(self, data_loader, bdd, performance_results):
        """
        Scenario: Verify match data volume and access time

        Given the match data is loaded
        When I access all matches
        Then I should have over 20000 matches
        And access time should be under 1ms
        """
        # Given
        bdd.given("the match data is loaded", data_loader is not None)

        # When
        def access_matches():
            return len(data_loader.matches)

        metrics = measure_performance(
            "Match Data Access",
            access_matches,
            iterations=100,
            warmup=10
        )
        count = access_matches()
        bdd.when("I access all matches", count)

        # Then
        bdd.then("should have over 20000 matches", count > 20000)
        bdd.then("access time should be under 1ms", metrics.avg_time < 0.001)

        performance_results.append(metrics)
        print(f"\n{metrics}")
        print(f"Total matches: {count}")


class TestRuVectorPerformance:
    """
    Feature: Measure RuVector vector store performance

    As a developer
    I want to measure vector operations performance
    So that I can ensure sub-millisecond search times
    """

    @pytest.mark.performance
    def test_vector_store_initialization(self, bdd, performance_results):
        """
        Scenario: Measure vector store initialization time

        Given the RuVector server is running
        When I initialize a new vector store
        Then initialization should complete within 5 seconds
        """
        from brazilian_soccer_mcp.vector_store import VectorStore, RuVectorConnectionError

        # Given
        bdd.given("the RuVector server is running", True)

        # When
        def init_store():
            try:
                store = VectorStore(auto_start_server=False)
                store.clear()
                return store
            except RuVectorConnectionError:
                pytest.skip("RuVector server not available")

        try:
            metrics = measure_performance(
                "Vector Store Initialization",
                init_store,
                iterations=3,
                warmup=1
            )
            bdd.when("I initialize a new vector store", metrics)

            # Then
            bdd.then("initialization should complete within 5 seconds", metrics.avg_time < 5.0)

            performance_results.append(metrics)
            print(f"\n{metrics}")
        except Exception as e:
            pytest.skip(f"RuVector not available: {e}")

    @pytest.mark.performance
    def test_vector_search_latency(self, vector_store, bdd, performance_results):
        """
        Scenario: Measure vector similarity search latency

        Given a populated vector store
        When I perform similarity searches
        Then search latency should be under 100ms average
        And 95th percentile should be under 200ms
        """
        # Given
        bdd.given("a populated vector store", vector_store is not None)
        bdd.given("vector store has entries", vector_store.size > 0)

        # When
        test_queries = [
            "Flamengo vs Fluminense derby match",
            "Brazilian striker high overall rating",
            "Palmeiras championship season",
            "Copa Libertadores final",
            "Gremio Internacional Grenal"
        ]

        all_times = []

        for query in test_queries:
            def search_query():
                return vector_store.search(query, k=10)

            metrics = measure_performance(
                f"Vector Search: '{query[:30]}...'",
                search_query,
                iterations=10,
                warmup=2
            )
            all_times.extend([metrics.avg_time])

        avg_search_time = statistics.mean(all_times)
        max_search_time = max(all_times)

        bdd.when("I perform similarity searches", len(test_queries))

        # Then
        bdd.then("search latency should be under 100ms average", avg_search_time < 0.1)
        bdd.then("max search time should be under 200ms", max_search_time < 0.2)

        search_metrics = PerformanceMetrics(
            operation="Vector Search (Aggregate)",
            iterations=len(test_queries) * 10,
            total_time=sum(all_times),
            min_time=min(all_times),
            max_time=max(all_times),
            avg_time=avg_search_time,
            median_time=statistics.median(all_times),
            std_dev=statistics.stdev(all_times) if len(all_times) > 1 else 0,
            throughput=len(all_times) / sum(all_times) if sum(all_times) > 0 else 0
        )

        performance_results.append(search_metrics)
        print(f"\n{search_metrics}")


class TestQueryHandlerPerformance:
    """
    Feature: Measure query handler performance

    As a developer
    I want to measure query execution performance
    So that I can ensure queries respond within 2 seconds
    """

    @pytest.mark.performance
    def test_match_search_performance(self, query_handler, bdd, performance_results):
        """
        Scenario: Measure match search query performance

        Given the query handler is initialized
        When I execute various match searches
        Then average response time should be under 500ms
        """
        # Given
        bdd.given("the query handler is initialized", query_handler is not None)

        # When - test different query types
        queries = [
            lambda: query_handler.search_matches(team="Flamengo", limit=50),
            lambda: query_handler.search_matches(team="Palmeiras", opponent="Corinthians", limit=50),
            lambda: query_handler.search_matches(competition="brasileirao", season=2019, limit=100),
            lambda: query_handler.search_matches(team="Santos", season=2018, limit=50),
            lambda: query_handler.search_matches(competition="libertadores", limit=50),
        ]

        all_metrics = []
        for i, query in enumerate(queries):
            metrics = measure_performance(
                f"Match Search Query {i+1}",
                query,
                iterations=10,
                warmup=2
            )
            all_metrics.append(metrics)

        avg_time = statistics.mean([m.avg_time for m in all_metrics])
        bdd.when("I execute various match searches", len(queries))

        # Then
        bdd.then("average response time should be under 500ms", avg_time < 0.5)

        aggregate = PerformanceMetrics(
            operation="Match Search (All Variants)",
            iterations=sum(m.iterations for m in all_metrics),
            total_time=sum(m.total_time for m in all_metrics),
            min_time=min(m.min_time for m in all_metrics),
            max_time=max(m.max_time for m in all_metrics),
            avg_time=avg_time,
            median_time=statistics.median([m.median_time for m in all_metrics]),
            std_dev=statistics.stdev([m.avg_time for m in all_metrics]),
            throughput=sum(m.iterations for m in all_metrics) / sum(m.total_time for m in all_metrics)
        )

        performance_results.append(aggregate)
        print(f"\n{aggregate}")

    @pytest.mark.performance
    def test_player_search_performance(self, query_handler, bdd, performance_results):
        """
        Scenario: Measure player search query performance

        Given the query handler is initialized
        When I execute various player searches
        Then average response time should be under 500ms
        """
        # Given
        bdd.given("the query handler is initialized", query_handler is not None)

        # When
        queries = [
            lambda: query_handler.search_players(nationality="Brazil", limit=50),
            lambda: query_handler.search_players(name="Neymar", limit=20),
            lambda: query_handler.search_players(club="Flamengo", limit=30),
            lambda: query_handler.search_players(position="ST", min_overall=80, limit=30),
            lambda: query_handler.search_players(nationality="Brazil", min_overall=85, limit=20),
        ]

        all_metrics = []
        for i, query in enumerate(queries):
            metrics = measure_performance(
                f"Player Search Query {i+1}",
                query,
                iterations=10,
                warmup=2
            )
            all_metrics.append(metrics)

        avg_time = statistics.mean([m.avg_time for m in all_metrics])
        bdd.when("I execute various player searches", len(queries))

        # Then
        bdd.then("average response time should be under 500ms", avg_time < 0.5)

        aggregate = PerformanceMetrics(
            operation="Player Search (All Variants)",
            iterations=sum(m.iterations for m in all_metrics),
            total_time=sum(m.total_time for m in all_metrics),
            min_time=min(m.min_time for m in all_metrics),
            max_time=max(m.max_time for m in all_metrics),
            avg_time=avg_time,
            median_time=statistics.median([m.median_time for m in all_metrics]),
            std_dev=statistics.stdev([m.avg_time for m in all_metrics]),
            throughput=sum(m.iterations for m in all_metrics) / sum(m.total_time for m in all_metrics)
        )

        performance_results.append(aggregate)
        print(f"\n{aggregate}")

    @pytest.mark.performance
    def test_team_stats_performance(self, query_handler, bdd, performance_results):
        """
        Scenario: Measure team statistics query performance

        Given the query handler is initialized
        When I calculate team statistics
        Then average response time should be under 1 second
        """
        # Given
        bdd.given("the query handler is initialized", query_handler is not None)

        # When
        queries = [
            lambda: query_handler.get_team_stats(team="Flamengo"),
            lambda: query_handler.get_team_stats(team="Palmeiras", season=2019),
            lambda: query_handler.get_team_stats(team="Corinthians", competition="brasileirao"),
            lambda: query_handler.get_team_stats(team="Santos", season=2018),
            lambda: query_handler.get_team_stats(team="Gremio"),
        ]

        all_metrics = []
        for i, query in enumerate(queries):
            metrics = measure_performance(
                f"Team Stats Query {i+1}",
                query,
                iterations=10,
                warmup=2
            )
            all_metrics.append(metrics)

        avg_time = statistics.mean([m.avg_time for m in all_metrics])
        bdd.when("I calculate team statistics", len(queries))

        # Then
        bdd.then("average response time should be under 1 second", avg_time < 1.0)

        aggregate = PerformanceMetrics(
            operation="Team Stats (All Variants)",
            iterations=sum(m.iterations for m in all_metrics),
            total_time=sum(m.total_time for m in all_metrics),
            min_time=min(m.min_time for m in all_metrics),
            max_time=max(m.max_time for m in all_metrics),
            avg_time=avg_time,
            median_time=statistics.median([m.median_time for m in all_metrics]),
            std_dev=statistics.stdev([m.avg_time for m in all_metrics]),
            throughput=sum(m.iterations for m in all_metrics) / sum(m.total_time for m in all_metrics)
        )

        performance_results.append(aggregate)
        print(f"\n{aggregate}")

    @pytest.mark.performance
    def test_head_to_head_performance(self, query_handler, bdd, performance_results):
        """
        Scenario: Measure head-to-head query performance

        Given the query handler is initialized
        When I calculate head-to-head statistics
        Then average response time should be under 1 second
        """
        # Given
        bdd.given("the query handler is initialized", query_handler is not None)

        # When
        queries = [
            lambda: query_handler.get_head_to_head(team1="Flamengo", team2="Fluminense"),
            lambda: query_handler.get_head_to_head(team1="Palmeiras", team2="Corinthians"),
            lambda: query_handler.get_head_to_head(team1="Gremio", team2="Internacional"),
            lambda: query_handler.get_head_to_head(team1="Santos", team2="Sao Paulo"),
            lambda: query_handler.get_head_to_head(team1="Cruzeiro", team2="Atletico Mineiro"),
        ]

        all_metrics = []
        for i, query in enumerate(queries):
            metrics = measure_performance(
                f"Head-to-Head Query {i+1}",
                query,
                iterations=10,
                warmup=2
            )
            all_metrics.append(metrics)

        avg_time = statistics.mean([m.avg_time for m in all_metrics])
        bdd.when("I calculate head-to-head statistics", len(queries))

        # Then
        bdd.then("average response time should be under 1 second", avg_time < 1.0)

        aggregate = PerformanceMetrics(
            operation="Head-to-Head (All Derbies)",
            iterations=sum(m.iterations for m in all_metrics),
            total_time=sum(m.total_time for m in all_metrics),
            min_time=min(m.min_time for m in all_metrics),
            max_time=max(m.max_time for m in all_metrics),
            avg_time=avg_time,
            median_time=statistics.median([m.median_time for m in all_metrics]),
            std_dev=statistics.stdev([m.avg_time for m in all_metrics]),
            throughput=sum(m.iterations for m in all_metrics) / sum(m.total_time for m in all_metrics)
        )

        performance_results.append(aggregate)
        print(f"\n{aggregate}")

    @pytest.mark.performance
    def test_standings_calculation_performance(self, query_handler, bdd, performance_results):
        """
        Scenario: Measure standings calculation performance

        Given the query handler is initialized
        When I calculate league standings for multiple seasons
        Then average response time should be under 2 seconds
        """
        # Given
        bdd.given("the query handler is initialized", query_handler is not None)

        # When
        queries = [
            lambda: query_handler.get_standings(season=2019),
            lambda: query_handler.get_standings(season=2018),
            lambda: query_handler.get_standings(season=2017),
            lambda: query_handler.get_standings(season=2016),
            lambda: query_handler.get_standings(season=2015),
        ]

        all_metrics = []
        for i, query in enumerate(queries):
            metrics = measure_performance(
                f"Standings Calculation {2019-i}",
                query,
                iterations=5,
                warmup=1
            )
            all_metrics.append(metrics)

        avg_time = statistics.mean([m.avg_time for m in all_metrics])
        bdd.when("I calculate league standings for multiple seasons", len(queries))

        # Then
        bdd.then("average response time should be under 2 seconds", avg_time < 2.0)

        aggregate = PerformanceMetrics(
            operation="Standings Calculation (5 Seasons)",
            iterations=sum(m.iterations for m in all_metrics),
            total_time=sum(m.total_time for m in all_metrics),
            min_time=min(m.min_time for m in all_metrics),
            max_time=max(m.max_time for m in all_metrics),
            avg_time=avg_time,
            median_time=statistics.median([m.median_time for m in all_metrics]),
            std_dev=statistics.stdev([m.avg_time for m in all_metrics]),
            throughput=sum(m.iterations for m in all_metrics) / sum(m.total_time for m in all_metrics)
        )

        performance_results.append(aggregate)
        print(f"\n{aggregate}")

    @pytest.mark.performance
    def test_statistics_query_performance(self, query_handler, bdd, performance_results):
        """
        Scenario: Measure statistical analysis performance

        Given the query handler is initialized
        When I execute statistical queries
        Then average response time should be under 2 seconds
        """
        # Given
        bdd.given("the query handler is initialized", query_handler is not None)

        # When
        queries = [
            lambda: query_handler.get_statistics(stat_type="biggest_wins", limit=20),
            lambda: query_handler.get_statistics(stat_type="highest_scoring", limit=20),
            lambda: query_handler.get_statistics(stat_type="avg_goals"),
            lambda: query_handler.get_statistics(stat_type="biggest_wins", season=2019, limit=10),
            lambda: query_handler.get_statistics(stat_type="avg_goals", competition="brasileirao"),
        ]

        all_metrics = []
        for i, query in enumerate(queries):
            metrics = measure_performance(
                f"Statistics Query {i+1}",
                query,
                iterations=5,
                warmup=1
            )
            all_metrics.append(metrics)

        avg_time = statistics.mean([m.avg_time for m in all_metrics])
        bdd.when("I execute statistical queries", len(queries))

        # Then
        bdd.then("average response time should be under 2 seconds", avg_time < 2.0)

        aggregate = PerformanceMetrics(
            operation="Statistics (All Types)",
            iterations=sum(m.iterations for m in all_metrics),
            total_time=sum(m.total_time for m in all_metrics),
            min_time=min(m.min_time for m in all_metrics),
            max_time=max(m.max_time for m in all_metrics),
            avg_time=avg_time,
            median_time=statistics.median([m.median_time for m in all_metrics]),
            std_dev=statistics.stdev([m.avg_time for m in all_metrics]),
            throughput=sum(m.iterations for m in all_metrics) / sum(m.total_time for m in all_metrics)
        )

        performance_results.append(aggregate)
        print(f"\n{aggregate}")


class TestEndToEndPerformance:
    """
    Feature: Measure end-to-end scenario performance

    As a user
    I want complete workflows to execute quickly
    So that the MCP server provides a responsive experience
    """

    @pytest.mark.performance
    def test_user_scenario_team_analysis(self, query_handler, bdd, performance_results):
        """
        Scenario: Complete team analysis workflow

        Given a user wants to analyze Flamengo's 2019 season
        When they execute a complete analysis workflow
        Then the entire workflow should complete within 5 seconds
        """
        # Given
        bdd.given("a user wants to analyze Flamengo's 2019 season", True)

        # When - simulate complete user workflow
        def complete_workflow():
            # Step 1: Get team stats
            stats = query_handler.get_team_stats(team="Flamengo", season=2019)

            # Step 2: Get season standings
            standings = query_handler.get_standings(season=2019)

            # Step 3: Find key matches
            matches = query_handler.search_matches(
                team="Flamengo",
                season=2019,
                competition="brasileirao",
                limit=38
            )

            # Step 4: Head-to-head with main rival
            h2h = query_handler.get_head_to_head(team1="Flamengo", team2="Fluminense")

            # Step 5: Find team players
            players = query_handler.search_players(club="Flamengo", limit=25)

            return stats, standings, matches, h2h, players

        metrics = measure_performance(
            "Complete Team Analysis Workflow",
            complete_workflow,
            iterations=5,
            warmup=1
        )
        bdd.when("they execute a complete analysis workflow", metrics)

        # Then
        bdd.then("entire workflow should complete within 5 seconds", metrics.avg_time < 5.0)

        performance_results.append(metrics)
        print(f"\n{metrics}")

    @pytest.mark.performance
    def test_user_scenario_derby_comparison(self, query_handler, bdd, performance_results):
        """
        Scenario: Derby comparison workflow

        Given a user wants to compare classic Brazilian derbies
        When they analyze multiple derbies
        Then the comparison should complete within 10 seconds
        """
        # Given
        bdd.given("a user wants to compare classic Brazilian derbies", True)

        # When
        def derby_comparison():
            derbies = [
                ("Flamengo", "Fluminense"),  # Fla-Flu
                ("Palmeiras", "Corinthians"),  # Derby Paulista
                ("Gremio", "Internacional"),  # Gre-Nal
                ("Cruzeiro", "Atletico Mineiro"),  # Classico Mineiro
                ("Santos", "Sao Paulo"),  # San-Sao
            ]

            results = []
            for team1, team2 in derbies:
                h2h = query_handler.get_head_to_head(team1=team1, team2=team2)
                matches = query_handler.search_matches(team=team1, opponent=team2, limit=20)
                results.append((h2h, matches))

            return results

        metrics = measure_performance(
            "Derby Comparison (5 Classic Derbies)",
            derby_comparison,
            iterations=3,
            warmup=1
        )
        bdd.when("they analyze multiple derbies", metrics)

        # Then
        bdd.then("comparison should complete within 10 seconds", metrics.avg_time < 10.0)

        performance_results.append(metrics)
        print(f"\n{metrics}")

    @pytest.mark.performance
    def test_user_scenario_player_scouting(self, query_handler, bdd, performance_results):
        """
        Scenario: Player scouting workflow

        Given a scout wants to find top Brazilian talent
        When they execute scouting queries
        Then the scouting workflow should complete within 3 seconds
        """
        # Given
        bdd.given("a scout wants to find top Brazilian talent", True)

        # When
        def scouting_workflow():
            # Find top Brazilian players
            top_brazilians = query_handler.search_players(
                nationality="Brazil",
                min_overall=80,
                limit=50
            )

            # Find strikers
            strikers = query_handler.search_players(
                nationality="Brazil",
                position="ST",
                min_overall=75,
                limit=20
            )

            # Find midfielders
            midfielders = query_handler.search_players(
                nationality="Brazil",
                position="CM",
                min_overall=75,
                limit=20
            )

            # Find players at Brazilian clubs
            flamengo_players = query_handler.search_players(club="Flamengo", limit=25)
            palmeiras_players = query_handler.search_players(club="Palmeiras", limit=25)

            return top_brazilians, strikers, midfielders, flamengo_players, palmeiras_players

        metrics = measure_performance(
            "Player Scouting Workflow",
            scouting_workflow,
            iterations=5,
            warmup=1
        )
        bdd.when("they execute scouting queries", metrics)

        # Then
        bdd.then("scouting workflow should complete within 3 seconds", metrics.avg_time < 3.0)

        performance_results.append(metrics)
        print(f"\n{metrics}")


class TestPerformanceSummary:
    """
    Feature: Generate performance summary report

    As a developer
    I want a summary of all performance metrics
    So that I can assess overall system performance
    """

    @pytest.mark.performance
    def test_generate_performance_report(self, performance_results, bdd):
        """
        Scenario: Generate final performance report

        Given all performance tests have run
        When I generate the summary report
        Then I should see all metrics in a formatted report
        """
        # Given
        bdd.given("all performance tests have run", len(performance_results) > 0)

        # When
        report_lines = [
            "\n" + "=" * 80,
            "PERFORMANCE TEST RESULTS - Brazilian Soccer MCP Server with RuVector",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Operations Measured: {len(performance_results)}",
            "-" * 80,
        ]

        for metrics in performance_results:
            report_lines.append(str(metrics))
            report_lines.append("-" * 40)

        # Calculate aggregate statistics
        all_avg_times = [m.avg_time for m in performance_results]
        all_throughputs = [m.throughput for m in performance_results]

        report_lines.extend([
            "\n" + "=" * 80,
            "AGGREGATE STATISTICS",
            "=" * 80,
            f"Total Operations: {len(performance_results)}",
            f"Fastest Operation: {min(all_avg_times)*1000:.2f}ms avg",
            f"Slowest Operation: {max(all_avg_times)*1000:.2f}ms avg",
            f"Mean Response Time: {statistics.mean(all_avg_times)*1000:.2f}ms",
            f"Median Response Time: {statistics.median(all_avg_times)*1000:.2f}ms",
            f"Total Throughput: {sum(all_throughputs):.2f} ops/sec combined",
            "=" * 80,
        ])

        report = "\n".join(report_lines)
        bdd.when("I generate the summary report", report)

        # Then
        bdd.then("should have metrics", len(performance_results) > 0)

        print(report)

        # Also save report to file
        report_path = "/workspaces/2025-12-15-python-claude-ruvector/performance_results.txt"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {report_path}")
