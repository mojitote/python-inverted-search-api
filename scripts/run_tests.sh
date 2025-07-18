#!/bin/bash

# Test runner script for Inverted Index Search API
# Usage: ./scripts/run_tests.sh [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
VERBOSE=false
COVERAGE=false
PARALLEL=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --test-type TYPE    Test type: all, unit, integration (default: all)"
    echo "  -v, --verbose          Run tests in verbose mode"
    echo "  -c, --coverage         Run tests with coverage report"
    echo "  -p, --parallel         Run tests in parallel"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Run all tests"
    echo "  $0 -t unit             # Run unit tests only"
    echo "  $0 -t integration -v   # Run integration tests with verbose output"
    echo "  $0 -c -p               # Run all tests with coverage and parallel execution"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--test-type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate test type
if [[ ! "$TEST_TYPE" =~ ^(all|unit|integration)$ ]]; then
    print_error "Invalid test type: $TEST_TYPE"
    print_error "Valid types: all, unit, integration"
    exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Please install it first:"
    print_error "pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi

# Build pytest command
PYTEST_CMD="pytest"

# Add test path based on type
case $TEST_TYPE in
    "unit")
        PYTEST_CMD="$PYTEST_CMD tests/test_index.py"
        ;;
    "integration")
        PYTEST_CMD="$PYTEST_CMD tests/test_api.py"
        ;;
    "all")
        PYTEST_CMD="$PYTEST_CMD tests/"
        ;;
esac

# Add options
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=html --cov-report=term-missing"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

# Add common options
PYTEST_CMD="$PYTEST_CMD --tb=short --strict-markers"

# Print test configuration
print_status "Running tests with configuration:"
echo "  Test Type: $TEST_TYPE"
echo "  Verbose: $VERBOSE"
echo "  Coverage: $COVERAGE"
echo "  Parallel: $PARALLEL"
echo "  Command: $PYTEST_CMD"
echo ""

# Run tests
print_status "Starting test execution..."
echo ""

if eval $PYTEST_CMD; then
    print_success "All tests passed!"
    
    if [ "$COVERAGE" = true ]; then
        print_status "Coverage report generated in htmlcov/index.html"
    fi
else
    print_error "Some tests failed!"
    exit 1
fi 