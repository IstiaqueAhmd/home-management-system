#!/bin/bash
# JWT Authentication Test Script (curl-based)
# Tests the enhanced JWT authentication system

BASE_URL="http://localhost:8000"
TEST_USERNAME="testuser_$(date +%s)"
TEST_EMAIL="test_$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"

echo "🚀 Testing JWT Authentication System"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

test_passed=0
test_total=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_status="$3"
    
    echo -e "\n${BLUE}--- $test_name ---${NC}"
    ((test_total++))
    
    response=$(eval "$test_command")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        ((test_passed++))
        echo "Response: $body"
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        echo "Expected status: $expected_status, Got: $status_code"
        echo "Response: $body"
    fi
}

# Test 1: Health Check
run_test "Health Check" \
    "curl -s -w \"%{http_code}\" \"$BASE_URL/health\"" \
    "200"

# Test 2: Registration
run_test "User Registration" \
    "curl -s -w \"%{http_code}\" -X POST \"$BASE_URL/register\" \
     -d \"username=$TEST_USERNAME\" \
     -d \"email=$TEST_EMAIL\" \
     -d \"full_name=Test User\" \
     -d \"password=$TEST_PASSWORD\" \
     --max-redirs 0" \
    "303"

# Test 3: Token Login
echo -e "\n${BLUE}--- API Token Login ---${NC}"
token_response=$(curl -s -X POST "$BASE_URL/token" \
    -d "username=$TEST_USERNAME" \
    -d "password=$TEST_PASSWORD")

if echo "$token_response" | grep -q "access_token"; then
    echo -e "${GREEN}✅ API Token Login PASSED${NC}"
    ((test_passed++))
    
    ACCESS_TOKEN=$(echo "$token_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$token_response" | grep -o '"refresh_token":"[^"]*"' | cut -d'"' -f4)
    
    echo "Access token: ${ACCESS_TOKEN:0:20}..."
    echo "Refresh token: ${REFRESH_TOKEN:0:20}..."
else
    echo -e "${RED}❌ API Token Login FAILED${NC}"
    echo "Response: $token_response"
fi
((test_total++))

# Test 4: Authenticated Request
if [ -n "$ACCESS_TOKEN" ]; then
    run_test "Authenticated Request (/me)" \
        "curl -s -w \"%{http_code}\" \"$BASE_URL/me\" \
         -H \"Authorization: Bearer $ACCESS_TOKEN\"" \
        "200"
else
    echo -e "${RED}❌ Skipping authenticated tests - no access token${NC}"
fi

# Test 5: Token Info
if [ -n "$ACCESS_TOKEN" ]; then
    run_test "Token Info" \
        "curl -s -w \"%{http_code}\" \"$BASE_URL/token-info\" \
         -H \"Authorization: Bearer $ACCESS_TOKEN\"" \
        "200"
fi

# Test 6: Token Refresh
if [ -n "$REFRESH_TOKEN" ]; then
    echo -e "\n${BLUE}--- Token Refresh ---${NC}"
    refresh_response=$(curl -s -X POST "$BASE_URL/refresh" \
        -H "Content-Type: application/json" \
        -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")
    
    if echo "$refresh_response" | grep -q "access_token"; then
        echo -e "${GREEN}✅ Token Refresh PASSED${NC}"
        ((test_passed++))
        NEW_ACCESS_TOKEN=$(echo "$refresh_response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        echo "New access token: ${NEW_ACCESS_TOKEN:0:20}..."
    else
        echo -e "${RED}❌ Token Refresh FAILED${NC}"
        echo "Response: $refresh_response"
    fi
    ((test_total++))
fi

# Test 7: Invalid Token
run_test "Invalid Token Test" \
    "curl -s -w \"%{http_code}\" \"$BASE_URL/me\" \
     -H \"Authorization: Bearer invalid_token_here\"" \
    "401"

# Test 8: Logout
if [ -n "$ACCESS_TOKEN" ]; then
    run_test "API Logout" \
        "curl -s -w \"%{http_code}\" -X POST \"$BASE_URL/logout\" \
         -H \"Authorization: Bearer $ACCESS_TOKEN\"" \
        "200"
fi

# Summary
echo -e "\n===================================="
echo -e "🏁 Tests completed: $test_passed/$test_total passed"

if [ $test_passed -eq $test_total ]; then
    echo -e "${GREEN}🎉 All tests passed! JWT authentication is working correctly.${NC}"
    exit 0
else
    echo -e "${RED}⚠️ $((test_total - test_passed)) tests failed. Check the output above for details.${NC}"
    exit 1
fi