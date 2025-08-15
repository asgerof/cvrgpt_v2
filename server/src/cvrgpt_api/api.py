import os
from fastapi import FastAPI, Depends, Query, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import List

from cvrgpt_core.models import Company, Filing, Accounts, CompareAccountsResponse
from cvrgpt_core.providers.base import Provider
from cvrgpt_core.services.accounts import compare
from cvrgpt_core.errors import NotFound, RateLimited, UpstreamBadData
from .cache import cache_json
from .logging_setup import RequestIdMiddleware


def get_provider() -> Provider:
    """Factory function to get the appropriate provider instance."""
    from .provider_factory import get_provider as _get_provider

    return _get_provider()


API_KEY = os.getenv("API_KEY")
ALLOWED_ORIGIN = os.getenv("CVRGPT_ALLOWED_ORIGIN", "http://localhost:3000")

app = FastAPI(title="CVRGPT API", version="0.1.0")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse({"error": "rate_limited"}, status_code=429)


def verify_api_key(x_api_key: str = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid_api_key")


# Error handlers
@app.exception_handler(NotFound)
async def not_found_handler(request: Request, exc: NotFound):
    return JSONResponse({"error": "not_found", "detail": str(exc)}, status_code=404)


@app.exception_handler(RateLimited)
async def rate_limited_handler(request: Request, exc: RateLimited):
    return JSONResponse({"error": "rate_limited", "detail": str(exc)}, status_code=429)


@app.exception_handler(UpstreamBadData)
async def upstream_bad_data_handler(request: Request, exc: UpstreamBadData):
    return JSONResponse({"error": "upstream_error", "detail": str(exc)}, status_code=502)


@app.get("/v1/search", response_model=List[Company])
@limiter.limit("60/minute")
def search_companies(
    request: Request,
    q: str = Query(..., min_length=2),
    provider: Provider = Depends(get_provider),
    _=Depends(verify_api_key),
):
    """Search for companies by name or CVR."""
    try:
        return provider.search_companies(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/company/{cvr}", response_model=Company)
@limiter.limit("120/minute")
def get_company(
    request: Request,
    cvr: str,
    provider: Provider = Depends(get_provider),
    _=Depends(verify_api_key),
):
    """Get company details by CVR."""
    try:
        return provider.get_company(cvr)
    except NotFound:
        raise HTTPException(
            status_code=404, detail={"error": "not_found", "detail": f"Company {cvr} not found"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/filings/{cvr}", response_model=List[Filing])
def list_filings(cvr: str, provider: Provider = Depends(get_provider)):
    """List filings for a company."""
    try:
        return provider.list_filings(cvr)
    except NotFound:
        raise HTTPException(
            status_code=404, detail={"error": "not_found", "detail": f"No filings found for {cvr}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/accounts/latest/{cvr}", response_model=Accounts)
@limiter.limit("30/minute")
def latest_accounts(
    request: Request,
    cvr: str,
    provider: Provider = Depends(get_provider),
    _=Depends(verify_api_key),
):
    """Get latest accounts for a company."""

    def _fetch():
        return provider.latest_accounts(cvr)

    try:
        return cache_json(f"latest_accounts:{cvr}", 6 * 3600, _fetch)
    except NotFound:
        raise HTTPException(
            status_code=404, detail={"error": "not_found", "detail": f"No accounts found for {cvr}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/compare/{cvr}", response_model=CompareAccountsResponse)
def compare_latest(cvr: str, provider: Provider = Depends(get_provider)):
    """Compare latest vs previous year accounts."""
    try:
        # Get latest accounts
        latest = provider.latest_accounts(cvr)

        # Get filings to find previous year
        filings = provider.list_filings(cvr)
        prev_years = sorted(
            {f.year for f in filings if f.type == "annual_report" and f.year < latest.year},
            reverse=True,
        )

        if not prev_years:
            raise HTTPException(
                status_code=404,
                detail={"error": "not_found", "detail": "Previous year not available"},
            )

        # Get previous year accounts
        previous = provider.accounts_for_year(cvr, prev_years[0])

        # Compare using core service
        return compare(latest, previous)

    except NotFound:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "detail": f"No comparison data for {cvr}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/healthz")
def health():
    """Health check endpoint."""
    return {"status": "ok", "provider": os.getenv("CVRGPT_PROVIDER", "fixture")}
