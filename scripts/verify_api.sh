#!/bin/bash
# API Verification Scripts
# Run these to verify the implementation works locally

BASE_URL="http://localhost:8000"

echo "=== Events API ==="
curl -s "$BASE_URL/v1/events?event_type=bankruptcy&nace=62&last_days=90&limit=5" | jq

echo -e "\n=== Tool Call ==="
curl -s -X POST "$BASE_URL/v1/tools/run" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "events_search",
    "args": {
      "event_type": "bankruptcy",
      "nace_prefixes": ["62"],
      "date_from": "2025-05-23T00:00:00",
      "date_to": "2025-08-23T00:00:00",
      "limit": 5
    }
  }' | jq

echo -e "\n=== Chat - Bankruptcies ==="
curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "demo",
    "messages": [
      {
        "role": "user",
        "content": "Give me recent bankruptcies in the IT sector (last 3 months)"
      }
    ]
  }' | jq

echo -e "\n=== Chat - Annual Result ==="
curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "demo",
    "messages": [
      {
        "role": "user",
        "content": "What was the annual result of Demo IT ApS in 2022?"
      }
    ]
  }' | jq
