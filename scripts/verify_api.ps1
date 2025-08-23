# API Verification Scripts
# Run these to verify the implementation works locally

$BASE_URL = "http://localhost:8000"

Write-Host "=== Events API ===" -ForegroundColor Green
$response = Invoke-RestMethod -Uri "$BASE_URL/v1/events?event_type=bankruptcy&nace=62&last_days=90&limit=5" -Method Get
$response | ConvertTo-Json -Depth 3

Write-Host "`n=== Tool Call ===" -ForegroundColor Green
$toolPayload = @{
    name = "events_search"
    args = @{
        event_type = "bankruptcy"
        nace_prefixes = @("62")
        date_from = "2025-05-23T00:00:00"
        date_to = "2025-08-23T00:00:00"
        limit = 5
    }
} | ConvertTo-Json -Depth 3

$response = Invoke-RestMethod -Uri "$BASE_URL/v1/tools/run" -Method Post -Body $toolPayload -ContentType "application/json"
$response | ConvertTo-Json -Depth 3

Write-Host "`n=== Chat - Bankruptcies ===" -ForegroundColor Green
$chatPayload = @{
    thread_id = "demo"
    messages = @(
        @{
            role = "user"
            content = "Give me recent bankruptcies in the IT sector (last 3 months)"
        }
    )
} | ConvertTo-Json -Depth 3

$response = Invoke-RestMethod -Uri "$BASE_URL/v1/chat" -Method Post -Body $chatPayload -ContentType "application/json"
$response | ConvertTo-Json -Depth 3

Write-Host "`n=== Chat - Annual Result ===" -ForegroundColor Green
$chatPayload = @{
    thread_id = "demo"
    messages = @(
        @{
            role = "user"
            content = "What was the annual result of Demo IT ApS in 2022?"
        }
    )
} | ConvertTo-Json -Depth 3

$response = Invoke-RestMethod -Uri "$BASE_URL/v1/chat" -Method Post -Body $chatPayload -ContentType "application/json"
$response | ConvertTo-Json -Depth 3
