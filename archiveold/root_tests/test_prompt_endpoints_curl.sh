#!/bin/bash

# Test script for Prompt API endpoints using curl
# Usage: ./test_prompt_endpoints_curl.sh [BASE_URL] [USERNAME] [PASSWORD]

BASE_URL="${1:-http://localhost:8000}"
USERNAME="${2:-${TEST_USERNAME}}"
PASSWORD="${3:-${TEST_PASSWORD}}"

echo "=========================================="
echo "PROMPT API ENDPOINTS TEST (CURL)"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "Username: ${USERNAME:-Not provided}"
echo "Password: ${PASSWORD:+Set}"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ACCESS_TOKEN=""

# Function to test server availability
test_server() {
    echo "1. Testing server availability..."
    if curl -s --max-time 5 "$BASE_URL/docs" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is accessible${NC}"
        return 0
    else
        echo -e "${RED}❌ Server is not accessible at $BASE_URL${NC}"
        return 1
    fi
}

# Function to authenticate and get token
authenticate() {
    if [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
        echo -e "${YELLOW}⚠️  No credentials provided - skipping authentication${NC}"
        echo "   Protected endpoints will fail"
        return 1
    fi

    echo "2. Authenticating..."
    
    # Try to get access token
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$USERNAME&password=$PASSWORD" 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$RESPONSE" | grep -q "access_token"; then
        ACCESS_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')
        echo -e "${GREEN}✅ Authentication successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Authentication failed${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
}

# Function to test an endpoint
test_endpoint() {
    local method="$1"
    local endpoint="$2"
    local description="$3"
    local auth_required="$4"
    
    echo ""
    echo "Testing: $description"
    echo "Endpoint: $method $endpoint"
    
    # Prepare curl command
    local curl_cmd="curl -s -w \"HTTP_STATUS:%{http_code}\" -X $method \"$BASE_URL$endpoint\""
    
    # Add auth header if token is available and auth is required
    if [ "$auth_required" = "true" ] && [ -n "$ACCESS_TOKEN" ]; then
        curl_cmd="curl -s -w \"HTTP_STATUS:%{http_code}\" -H \"Authorization: Bearer $ACCESS_TOKEN\" -X $method \"$BASE_URL$endpoint\""
    fi
    
    # Execute request
    local response=$(eval $curl_cmd 2>/dev/null)
    local http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | sed 's/HTTP_STATUS://')
    local body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    # Check result
    if [ -z "$http_status" ]; then
        echo -e "${RED}❌ Request failed - no response${NC}"
        return 1
    elif [ "$http_status" -ge 200 ] && [ "$http_status" -lt 300 ]; then
        echo -e "${GREEN}✅ Success (Status: $http_status)${NC}"
        
        # Try to count items if it's a JSON array
        if echo "$body" | grep -q '^\['; then
            local count=$(echo "$body" | grep -o '{"' | wc -l)
            echo "   Response: JSON array with $count items"
        elif [ ${#body} -gt 100 ]; then
            echo "   Response: ${body:0:100}..."
        else
            echo "   Response: $body"
        fi
        return 0
    else
        echo -e "${RED}❌ Failed (Status: $http_status)${NC}"
        if [ ${#body} -gt 200 ]; then
            echo "   Error: ${body:0:200}..."
        else
            echo "   Error: $body"
        fi
        return 1
    fi
}

# Main test execution
main() {
    # Test server availability
    if ! test_server; then
        echo -e "${RED}Cannot proceed - server is not available${NC}"
        exit 1
    fi
    
    # Try to authenticate
    authenticate
    local auth_success=$?
    
    echo ""
    echo "3. Testing Prompt API endpoints..."
    echo "=========================================="
    
    local total_tests=0
    local passed_tests=0
    
    # Test my-prompts endpoint
    ((total_tests++))
    if test_endpoint "GET" "/api/v1/prompts/my-prompts" "My Prompts" "true"; then
        ((passed_tests++))
    fi
    
    # Test my-prompts with query parameters
    ((total_tests++))
    if test_endpoint "GET" "/api/v1/prompts/my-prompts?skip=0&limit=10&filter_is_active=true" "My Prompts (filtered)" "true"; then
        ((passed_tests++))
    fi
    
    # Test shared prompts endpoint
    ((total_tests++))
    if test_endpoint "GET" "/api/v1/prompts/shared" "Shared Prompts" "true"; then
        ((passed_tests++))
    fi
    
    # Test shared prompts with query parameters
    ((total_tests++))
    if test_endpoint "GET" "/api/v1/prompts/shared?skip=0&limit=10&filter_is_active=true" "Shared Prompts (filtered)" "true"; then
        ((passed_tests++))
    fi
    
    # Test prompts root (should require authentication)
    ((total_tests++))
    if test_endpoint "GET" "/api/v1/prompts/" "Prompts Root" "true"; then
        ((passed_tests++))
    fi
    
    # Summary
    echo ""
    echo "=========================================="
    echo "TEST SUMMARY"
    echo "=========================================="
    echo "Total tests: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $((total_tests - passed_tests))"
    
    if [ $auth_success -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Note: Authentication failed - protected endpoints may have failed due to missing auth${NC}"
    fi
    
    if [ $passed_tests -eq $total_tests ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed${NC}"
        exit 1
    fi
}

# Run main function
main