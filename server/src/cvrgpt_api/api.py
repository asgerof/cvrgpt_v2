from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from cvrgpt_core.models import Company, Filing, Accounts, CompareAccountsResponse
from cvrgpt_core.providers.fixture import FixtureProvider
from cvrgpt_core.errors import NotFound, RateLimited, UpstreamBadData
from cvrgpt_core.services.accounts import compare as compare_accounts

def get_provider():
    # TODO: read env PROVIDER; for now always fixture
    return FixtureProvider()

app = FastAPI(title="CVRGPT API")

@app.get("/companies/search", response_model=List[Company])
def search_companies(q: str = Query(..., min_length=2), p=Depends(get_provider)):
    return p.search_companies(q)

@app.get("/companies/{cvr}", response_model=Company)
def get_company(cvr: str, p=Depends(get_provider)):
    return p.get_company(cvr)

@app.get("/companies/{cvr}/filings", response_model=List[Filing])
def list_filings(cvr: str, p=Depends(get_provider)):
    return p.list_filings(cvr)

@app.get("/companies/{cvr}/accounts/latest", response_model=Accounts)
def latest_accounts(cvr: str, p=Depends(get_provider)):
    return p.latest_accounts(cvr)

@app.get("/companies/{cvr}/accounts/compare", response_model=CompareAccountsResponse)
def compare_latest(cvr: str, p=Depends(get_provider)):
    a = p.latest_accounts(cvr)      # latest
    b = Accounts(year=a.year-1)     # TODO: fixture second year, simple stub
    return compare_accounts(a, b)

# Error handlers
@app.exception_handler(NotFound)
async def _nf(_, exc): 
    return JSONResponse({"error": "not_found", "detail": str(exc)}, status_code=404)

@app.exception_handler(RateLimited)
async def _rl(_, exc): 
    return JSONResponse({"error": "rate_limited"}, status_code=429)

@app.exception_handler(UpstreamBadData)
async def _bd(_, exc): 
    return JSONResponse({"error": "bad_upstream"}, status_code=502)
