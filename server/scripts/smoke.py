#!/usr/bin/env python3
"""
Smoke test script for CVRGPT API endpoints.
Tests basic functionality against live or fixture data.
"""

import httpx
import sys
import os
from typing import Dict, Any

BASE_URL = os.environ.get("SMOKE_TEST_URL", "http://localhost:8000")
TEST_CVR = "10150817"  # Erhvervsstyrelsen


async def smoke_test():
    """Run smoke tests against key endpoints."""
    print(f"🔥 Running smoke tests against {BASE_URL}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tests = [
            ("Health Check", "GET", "/healthz"),
            ("Search Companies", "GET", f"/v1/search?q={TEST_CVR}"),
            ("Get Company", "GET", f"/v1/company/{TEST_CVR}"),
            ("List Filings", "GET", f"/v1/filings/{TEST_CVR}"),
            ("Latest Accounts", "GET", f"/v1/accounts/latest/{TEST_CVR}"),
            ("Compare Accounts", "GET", f"/v1/compare/{TEST_CVR}"),
        ]
        
        results = []
        
        for test_name, method, endpoint in tests:
            try:
                url = f"{BASE_URL}{endpoint}"
                print(f"  Testing {test_name}... ", end="", flush=True)
                
                response = await client.request(method, url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {response.status_code}")
                    results.append((test_name, True, response.status_code, len(str(data))))
                else:
                    print(f"❌ {response.status_code}")
                    results.append((test_name, False, response.status_code, len(response.text)))
                    
            except Exception as e:
                print(f"💥 {str(e)[:50]}")
                results.append((test_name, False, 0, str(e)[:100]))
        
        # Summary
        print("\n📊 Results:")
        passed = sum(1 for _, success, _, _ in results if success)
        total = len(results)
        
        for test_name, success, status, info in results:
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {test_name:<20} {status:<3} ({info})")
        
        print(f"\n🎯 {passed}/{total} tests passed")
        
        if passed < total:
            print("❌ Some tests failed")
            sys.exit(1)
        else:
            print("✅ All tests passed!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(smoke_test())
