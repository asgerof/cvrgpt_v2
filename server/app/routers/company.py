from fastapi import APIRouter, Depends, Response, Query, HTTPException
from app.security import require_api_key
from app.models.company import (
    Company,
    SearchResponse,
    FilingsResponse,
    AccountSummary,
    CompareResponse,
)
from app.validators import assert_cvr
from app.cache import cache_get, cache_set
from app.http_headers import set_cache_headers
import json

router = APIRouter(prefix="/v1", tags=["v1"])


@router.get("/search", response_model=SearchResponse, dependencies=[Depends(require_api_key)])
async def search(q: str = Query(..., min_length=2), limit: int = 10, cursor: str | None = None):
    cached = await cache_get("search", q=q, limit=limit, cursor=cursor)
    if cached:
        return json.loads(cached)
    # Using fixture data for demo - replace with real provider in production
    resp = {
        "items": [{"cvr": "12345678", "name": "Demo A/S", "snippet": None, "sources": []}],
        "next_cursor": None,
        "has_more": False,
    }
    await cache_set("search", json.dumps(resp), q=q, limit=limit, cursor=cursor)
    return resp


@router.get("/company/{cvr}", response_model=Company, dependencies=[Depends(require_api_key)])
async def company(cvr: str):
    try:
        assert_cvr(cvr)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    # Using fixture data for demo - integrate with provider system
    return {"cvr": cvr, "name": "Demo A/S", "status": "ACTIVE", "address": None, "sources": []}


@router.get(
    "/filings/{cvr}", response_model=FilingsResponse, dependencies=[Depends(require_api_key)]
)
async def filings(cvr: str, limit: int = 20, cursor: str | None = None):
    try:
        assert_cvr(cvr)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"items": [], "next_cursor": None, "has_more": False}


@router.get(
    "/accounts/latest/{cvr}", response_model=AccountSummary, dependencies=[Depends(require_api_key)]
)
async def accounts_latest(cvr: str):
    assert_cvr(cvr)
    return {
        "cvr": cvr,
        "fiscal_year": "2024",
        "revenue": None,
        "ebit": None,
        "equity": None,
        "currency": "DKK",
        "sources": [],
    }


@router.get(
    "/compare/{cvr}", response_model=CompareResponse, dependencies=[Depends(require_api_key)]
)
async def compare(cvr: str):
    assert_cvr(cvr)
    return {
        "base": {
            "cvr": cvr,
            "fiscal_year": "2024",
            "revenue": 0,
            "ebit": 0,
            "equity": 0,
            "currency": "DKK",
            "sources": [],
        },
        "peers": [],
        "sources": [],
    }


@router.get("/compare/{cvr}/export", dependencies=[Depends(require_api_key)])
async def compare_export(cvr: str):
    assert_cvr(cvr)
    # CSV body (replace with real data)
    csv = "cvr,name,revenue_delta,ebit_delta\n" + f"{cvr},Demo A/S,,\n"
    body = csv.encode("utf-8")
    resp = Response(content=body, media_type="text/csv; charset=utf-8")
    resp.headers["Content-Disposition"] = f'attachment; filename="compare-{cvr}.csv"'
    set_cache_headers(resp, body)
    return resp
