import os
from fastapi import FastAPI, Depends, Query, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import List
from cvrgpt_core.models import Company, Filing, Accounts, CompareAccountsResponse
from cvrgpt_core.errors import NotFound, RateLimited, UpstreamBadData
from cvrgpt_core.services.accounts import compare as compare_accounts
from .cache import cache_json
from .provider_factory import get_provider as get_provider_instance

API_KEY = os.getenv("API_KEY")

def verify_api_key(x_api_key: str = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid_api_key")

def get_provider():
    return get_provider_instance()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="CVRGPT API")
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/companies/search", response_model=List[Company])
@limiter.limit("60/minute")
def search_companies(request: Request, q: str = Query(..., min_length=2), p=Depends(get_provider)):
    return p.search_companies(q)

@app.get("/companies/{cvr}", response_model=Company)
@limiter.limit("120/minute")
def get_company(request: Request, cvr: str, p=Depends(get_provider)):
    return p.get_company(cvr)

@app.get("/companies/{cvr}/filings", response_model=List[Filing])
@limiter.limit("60/minute")
def list_filings(request: Request, cvr: str, p=Depends(get_provider)):
    return p.list_filings(cvr)

@app.get("/companies/{cvr}/accounts/latest", response_model=Accounts)
@limiter.limit("30/minute")
def latest_accounts(request: Request, cvr: str, p=Depends(get_provider)):
    def _produce():
        return p.latest_accounts(cvr)
    return cache_json(f"latest_accounts:{cvr}", ttl=6*3600, producer=_produce)

@app.get("/companies/{cvr}/accounts/compare", response_model=CompareAccountsResponse)
def compare_latest(cvr: str, p=Depends(get_provider)):
    a = p.latest_accounts(cvr)      # latest
    b = Accounts(year=a.year-1)     # TODO: fixture second year, simple stub
    return compare_accounts(a, b)

# Error handlers
@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"error": "rate_limited"}, status_code=429)

@app.exception_handler(NotFound)
async def _nf(_, exc): 
    return JSONResponse({"error": "not_found", "detail": str(exc)}, status_code=404)

@app.exception_handler(RateLimited)
async def _rl(_, exc): 
    return JSONResponse({"error": "rate_limited"}, status_code=429)

@app.exception_handler(UpstreamBadData)
async def _bd(_, exc): 
    return JSONResponse({"error": "bad_upstream"}, status_code=502)
