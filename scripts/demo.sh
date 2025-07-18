#!/bin/bash

# Demo script for Inverted Index Search API
# This script demonstrates the API functionality with sample documents

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API base URL
API_URL="http://localhost:8000"

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

# Function to check if API is running
check_api() {
    if ! curl -s "$API_URL/health" > /dev/null; then
        print_error "API is not running at $API_URL"
        print_error "Please start the API first: python -m app.main"
        exit 1
    fi
    print_success "API is running at $API_URL"
}

# Function to make API requests
api_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "$API_URL$endpoint"
    fi
}

# Function to pretty print JSON
pretty_json() {
    python3 -m json.tool
}

# Main demo function
run_demo() {
    print_status "Starting Inverted Index Search API Demo"
    echo ""
    
    # Check if API is running
    check_api
    echo ""
    
    # Sample documents
    print_status "1. Uploading sample documents..."
    
    documents=(
        '{"doc_id": "python_intro", "content": "Python is a high-level programming language known for its simplicity and readability. It is widely used in web development, data science, and artificial intelligence.", "title": "Python Introduction", "author": "John Doe"}'
        '{"doc_id": "fastapi_guide", "content": "FastAPI is a modern web framework for building APIs with Python. It offers automatic documentation, type checking, and high performance.", "title": "FastAPI Guide", "author": "Jane Smith"}'
        '{"doc_id": "search_engines", "content": "Search engines use inverted indexes to efficiently find documents containing specific terms. This data structure maps words to document lists.", "title": "Search Engine Basics", "author": "Bob Johnson"}'
        '{"doc_id": "machine_learning", "content": "Machine learning algorithms can process large datasets to find patterns and make predictions. Python is the most popular language for ML.", "title": "Machine Learning Overview", "author": "Alice Brown"}'
        '{"doc_id": "web_development", "content": "Web development involves creating websites and web applications. Popular technologies include HTML, CSS, JavaScript, and Python frameworks like Django and Flask.", "title": "Web Development Guide", "author": "Charlie Wilson"}'
    )
    
    for doc in "${documents[@]}"; do
        response=$(api_request "POST" "/upload" "$doc")
        doc_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['doc_id'])")
        print_success "Uploaded document: $doc_id"
    done
    echo ""
    
    # Show index statistics
    print_status "2. Viewing index statistics..."
    api_request "GET" "/index" | pretty_json
    echo ""
    
    # Search demonstrations
    print_status "3. Searching for 'python'..."
    api_request "GET" "/search?query=python&limit=3" | pretty_json
    echo ""
    
    print_status "4. Searching for 'web development'..."
    api_request "GET" "/search?query=web development&limit=3" | pretty_json
    echo ""
    
    print_status "5. Searching for 'machine learning'..."
    api_request "GET" "/search?query=machine learning&limit=3" | pretty_json
    echo ""
    
    print_status "6. Searching for 'fastapi'..."
    api_request "GET" "/search?query=fastapi&limit=3" | pretty_json
    echo ""
    
    # Get specific document
    print_status "7. Retrieving specific document..."
    api_request "GET" "/documents/python_intro" | pretty_json
    echo ""
    
    # Search with no results
    print_status "8. Searching for non-existent term..."
    api_request "GET" "/search?query=javascript&limit=3" | pretty_json
    echo ""
    
    # Delete a document
    print_status "9. Deleting a document..."
    api_request "DELETE" "/documents/machine_learning" | pretty_json
    echo ""
    
    # Search again to show deletion effect
    print_status "10. Searching after deletion..."
    api_request "GET" "/search?query=machine learning&limit=3" | pretty_json
    echo ""
    
    # Final index statistics
    print_status "11. Final index statistics..."
    api_request "GET" "/index" | pretty_json
    echo ""
    
    print_success "Demo completed successfully!"
    print_status "You can explore the API further at: $API_URL/docs"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -u, --url URL          API base URL (default: http://localhost:8000)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Run demo with default settings"
    echo "  $0 -u http://api.example.com  # Run demo with custom API URL"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            API_URL="$2"
            shift 2
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

# Check if curl is available
if ! command -v curl &> /dev/null; then
    print_error "curl is not installed. Please install it first."
    exit 1
fi

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed. Please install it first."
    exit 1
fi

# Run the demo
run_demo 