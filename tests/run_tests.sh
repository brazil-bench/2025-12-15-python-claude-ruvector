#!/bin/bash
###############################################################################
# Brazilian Soccer MCP Server - Test Runner Script
#
# This script provides convenient commands to run different test suites
# with various options for the BDD test scenarios.
#
# Usage:
#   ./run_tests.sh              # Run all tests
#   ./run_tests.sh match        # Run match query tests
#   ./run_tests.sh team         # Run team query tests
#   ./run_tests.sh player       # Run player query tests
#   ./run_tests.sh stats        # Run statistics tests
#   ./run_tests.sh coverage     # Run with coverage report
#   ./run_tests.sh verbose      # Run with verbose output
#   ./run_tests.sh quick        # Run quick tests only (exclude slow)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Brazilian Soccer MCP Server - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse command line arguments
TEST_TYPE="${1:-all}"

case "$TEST_TYPE" in
    all)
        echo -e "${GREEN}Running all tests...${NC}"
        pytest tests/ -v
        ;;

    match)
        echo -e "${GREEN}Running match query tests...${NC}"
        pytest tests/test_match_queries.py -v
        ;;

    team)
        echo -e "${GREEN}Running team query tests...${NC}"
        pytest tests/test_team_queries.py -v
        ;;

    player)
        echo -e "${GREEN}Running player query tests...${NC}"
        pytest tests/test_player_queries.py -v
        ;;

    stats|statistics)
        echo -e "${GREEN}Running statistics tests...${NC}"
        pytest tests/test_statistics.py -v
        ;;

    coverage)
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest tests/ \
            --cov=src/brazilian_soccer_mcp \
            --cov-report=html \
            --cov-report=term-missing \
            -v
        echo ""
        echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"
        ;;

    verbose)
        echo -e "${GREEN}Running tests with verbose output...${NC}"
        pytest tests/ -vv --tb=long
        ;;

    quick)
        echo -e "${GREEN}Running quick tests (excluding slow tests)...${NC}"
        pytest tests/ -v -m "not slow"
        ;;

    derby)
        echo -e "${GREEN}Running derby match tests...${NC}"
        pytest tests/ -v -m derby
        ;;

    integration)
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest tests/ -v -m integration
        ;;

    brasileirao)
        echo -e "${GREEN}Running Brasileirão-specific tests...${NC}"
        pytest tests/ -v -m brasileirao
        ;;

    specific)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please provide a test file or class name${NC}"
            echo "Usage: ./run_tests.sh specific <test_file_or_class>"
            exit 1
        fi
        echo -e "${GREEN}Running specific test: $2${NC}"
        pytest "$2" -v
        ;;

    failed)
        echo -e "${GREEN}Re-running failed tests...${NC}"
        pytest tests/ -v --lf
        ;;

    help|--help|-h)
        echo "Brazilian Soccer MCP Server - Test Runner"
        echo ""
        echo "Usage: ./run_tests.sh [OPTION]"
        echo ""
        echo "Options:"
        echo "  all           Run all tests (default)"
        echo "  match         Run match query tests"
        echo "  team          Run team query tests"
        echo "  player        Run player query tests"
        echo "  stats         Run statistics tests"
        echo "  coverage      Run tests with coverage report"
        echo "  verbose       Run tests with verbose output"
        echo "  quick         Run quick tests only (exclude slow)"
        echo "  derby         Run derby match tests"
        echo "  integration   Run integration tests"
        echo "  brasileirao   Run Brasileirão-specific tests"
        echo "  specific FILE Run specific test file or class"
        echo "  failed        Re-run only failed tests"
        echo "  help          Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh"
        echo "  ./run_tests.sh match"
        echo "  ./run_tests.sh coverage"
        echo "  ./run_tests.sh specific tests/test_match_queries.py::TestFindDerbyMatches"
        exit 0
        ;;

    *)
        echo -e "${RED}Error: Unknown test type '$TEST_TYPE'${NC}"
        echo "Run './run_tests.sh help' for usage information"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}All tests passed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Some tests failed!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
