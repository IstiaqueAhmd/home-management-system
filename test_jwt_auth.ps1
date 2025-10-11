# JWT Authentication Test Script (PowerShell)
# Tests the enhanced JWT authentication system

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$TestUsername = "testuser_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$TestEmail = "test_$(Get-Date -Format 'yyyyMMdd_HHmmss')@example.com"
$TestPassword = "TestPass123!"

Write-Host "🚀 Testing JWT Authentication System" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$TestPassed = 0
$TestTotal = 0

function Run-Test {
    param(
        [string]$TestName,
        [scriptblock]$TestCommand,
        [int]$ExpectedStatus
    )
    
    Write-Host "`n--- $TestName ---" -ForegroundColor Blue
    $global:TestTotal++
    
    try {
        $result = & $TestCommand
        $statusCode = $result.StatusCode
        $body = $result.Content
        
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "✅ $TestName PASSED" -ForegroundColor Green
            $global:TestPassed++
            Write-Host "Response: $($body | ConvertFrom-Json | ConvertTo-Json -Compress)"
        } else {
            Write-Host "❌ $TestName FAILED" -ForegroundColor Red
            Write-Host "Expected status: $ExpectedStatus, Got: $statusCode"
            Write-Host "Response: $body"
        }
    } catch {
        Write-Host "💥 $TestName ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Invoke-RestMethodSafe {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [object]$Body = $null,
        [string]$ContentType = "application/json"
    )
    
    try {
        $params = @{
            Uri = $Uri
            Method = $Method
            Headers = $Headers
            UseBasicParsing = $true
        }
        
        if ($Body) {
            if ($Body -is [hashtable]) {
                $params.Body = ($Body | ConvertTo-Json)
                $params.ContentType = $ContentType
            } else {
                $params.Body = $Body
            }
        }
        
        $response = Invoke-WebRequest @params
        return @{
            StatusCode = $response.StatusCode
            Content = $response.Content
        }
    } catch {
        return @{
            StatusCode = $_.Exception.Response.StatusCode.Value__
            Content = $_.Exception.Message
        }
    }
}

# Test 1: Health Check
Run-Test "Health Check" {
    Invoke-RestMethodSafe -Uri "$BaseUrl/health"
} 200

# Test 2: Registration
Run-Test "User Registration" {
    $body = "username=$TestUsername&email=$TestEmail&full_name=Test User&password=$TestPassword"
    Invoke-RestMethodSafe -Uri "$BaseUrl/register" -Method POST -Body $body -ContentType "application/x-www-form-urlencoded"
} 303

# Test 3: Token Login
Write-Host "`n--- API Token Login ---" -ForegroundColor Blue
$TestTotal++

try {
    $body = "username=$TestUsername&password=$TestPassword"
    $tokenResponse = Invoke-RestMethodSafe -Uri "$BaseUrl/token" -Method POST -Body $body -ContentType "application/x-www-form-urlencoded"
    
    if ($tokenResponse.StatusCode -eq 200) {
        Write-Host "✅ API Token Login PASSED" -ForegroundColor Green
        $TestPassed++
        
        $tokenData = $tokenResponse.Content | ConvertFrom-Json
        $global:AccessToken = $tokenData.access_token
        $global:RefreshToken = $tokenData.refresh_token
        
        Write-Host "Access token: $($AccessToken.Substring(0, 20))..."
        Write-Host "Refresh token: $($RefreshToken.Substring(0, 20))..."
    } else {
        Write-Host "❌ API Token Login FAILED" -ForegroundColor Red
        Write-Host "Response: $($tokenResponse.Content)"
    }
} catch {
    Write-Host "💥 API Token Login ERROR: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Authenticated Request
if ($AccessToken) {
    Run-Test "Authenticated Request (/me)" {
        $headers = @{ "Authorization" = "Bearer $AccessToken" }
        Invoke-RestMethodSafe -Uri "$BaseUrl/me" -Headers $headers
    } 200
}

# Test 5: Token Info
if ($AccessToken) {
    Run-Test "Token Info" {
        $headers = @{ "Authorization" = "Bearer $AccessToken" }
        Invoke-RestMethodSafe -Uri "$BaseUrl/token-info" -Headers $headers
    } 200
}

# Test 6: Token Refresh
if ($RefreshToken) {
    Write-Host "`n--- Token Refresh ---" -ForegroundColor Blue
    $TestTotal++
    
    try {
        $body = @{ refresh_token = $RefreshToken }
        $refreshResponse = Invoke-RestMethodSafe -Uri "$BaseUrl/refresh" -Method POST -Body $body
        
        if ($refreshResponse.StatusCode -eq 200) {
            Write-Host "✅ Token Refresh PASSED" -ForegroundColor Green
            $TestPassed++
            
            $refreshData = $refreshResponse.Content | ConvertFrom-Json
            $NewAccessToken = $refreshData.access_token
            Write-Host "New access token: $($NewAccessToken.Substring(0, 20))..."
        } else {
            Write-Host "❌ Token Refresh FAILED" -ForegroundColor Red
            Write-Host "Response: $($refreshResponse.Content)"
        }
    } catch {
        Write-Host "💥 Token Refresh ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Test 7: Invalid Token
Run-Test "Invalid Token Test" {
    $headers = @{ "Authorization" = "Bearer invalid_token_here" }
    Invoke-RestMethodSafe -Uri "$BaseUrl/me" -Headers $headers
} 401

# Test 8: Logout
if ($AccessToken) {
    Run-Test "API Logout" {
        $headers = @{ "Authorization" = "Bearer $AccessToken" }
        Invoke-RestMethodSafe -Uri "$BaseUrl/logout" -Method POST -Headers $headers
    } 200
}

# Summary
Write-Host "`n====================================" -ForegroundColor Cyan
Write-Host "🏁 Tests completed: $TestPassed/$TestTotal passed" -ForegroundColor Cyan

if ($TestPassed -eq $TestTotal) {
    Write-Host "🎉 All tests passed! JWT authentication is working correctly." -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️ $($TestTotal - $TestPassed) tests failed. Check the output above for details." -ForegroundColor Red
    exit 1
}