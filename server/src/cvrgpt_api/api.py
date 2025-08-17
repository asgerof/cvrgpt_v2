from fastapi import FastAPI, HTTPException, Request, Depends, APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .logging import setup_logging, access_log_mw
from .security import require_api_key
from .observability import RequestIDMiddleware
from .redis_client import redis_client
from .rate_limit import init_rate_limiter
from fastapi_limiter.depends import RateLimiter
from .cache import cache_get, cache_set, with_etag
from .providers.fixtures import FixtureProvider
from .providers.cvr_api import CVRApiProvider
from .providers.regnskab import RegnskabProvider
from .providers.base import CompositeProvider
from .services.compare import compare_accounts_snapshots
from .mcp_server import mcp
from . import models
from .errors import ErrorPayload, ErrorCode
from cvrgpt_api import metrics
import csv
import io

log = setup_logging()

_provider_instance = None


def get_provider():
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance
    if settings.provider == "fixtures":
        # For fixtures, use a composite with fixture provider for both core and filings
        fixture_provider = FixtureProvider()
        _provider_instance = CompositeProvider(
            core=fixture_provider, filings_provider=fixture_provider
        )
    elif settings.provider == "cvr_api":
        if not settings.api_base_url:
            raise RuntimeError("CVR API requires CVRGPT_API_BASE_URL")
        core = CVRApiProvider(
            settings.api_base_url, settings.api_key, settings.api_user, settings.api_password
        )
        filings = RegnskabProvider()
        _provider_instance = CompositeProvider(core=core, filings_provider=filings)
    else:
        raise RuntimeError(f"Unknown provider: {settings.provider}")
    return _provider_instance


app = FastAPI(title="CVRGPT Server", version="0.1.0")

# Create versioned router with API key protection
api_v1 = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Wire up access logging
app.add_middleware(BaseHTTPMiddleware, dispatch=access_log_mw)

# Wire up metrics
app.include_router(metrics.router)

# CORS so the Next.js dev server can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP SSE at /mcp
app.mount(settings.mcp_mount_path, mcp.sse_app())

# Include the versioned API router
app.include_router(api_v1)


@app.on_event("startup")
async def _startup():
    await init_rate_limiter()


# Request ID middleware is now handled by RequestIDMiddleware class above


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize error payloads
    code = (
        ErrorCode.BAD_REQUEST
        if exc.status_code == 400
        else (
            ErrorCode.NOT_FOUND
            if exc.status_code == 404
            else (ErrorCode.UPSTREAM_ERROR if exc.status_code == 502 else ErrorCode.UPSTREAM_ERROR)
        )
    )
    message = "An error occurred"
    detail = None
    if isinstance(exc.detail, dict) and exc.detail.get("detail"):
        detail = exc.detail.get("detail")
        message = detail or message
    elif isinstance(exc.detail, str):
        message = exc.detail
    payload = ErrorPayload(code=code, message=message, detail=detail).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)


@app.get("/healthz", response_model=dict)
async def health():
    return {"status": "ok", "provider": settings.provider}


@app.get("/readyz", response_model=dict)
async def readiness():
    try:
        pong = await redis_client.ping()
        if pong:
            return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Redis unavailable")


@api_v1.get(
    "/search",
    response_model=models.SearchResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
)
async def search(q: str, limit: int = 10):
    prov = get_provider()
    try:
        data = await prov.search_companies(q, limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    data.pop("x_cache", None)  # Remove cache info for clean response
    return JSONResponse(data)


TTL_COMPANY = 6 * 60 * 60  # 6 hours


@api_v1.get(
    "/company/{cvr}",
    response_model=models.CompanyResponse,
    dependencies=[Depends(RateLimiter(times=60, seconds=60))],
)
async def company(cvr: str, request: Request):
    key = f"v1:company:{cvr}"
    cached = await cache_get(key)
    if cached:
        return with_etag(request, cached, TTL_COMPANY)

    prov = get_provider()
    try:
        data = await prov.get_company(cvr)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=ErrorPayload(
                code=ErrorCode.NOT_FOUND, message=f"Company {cvr} not found"
            ).model_dump(),
        )
    except Exception as e:
        log.error(f"Company lookup failed for {cvr}: {e}")
        raise HTTPException(
            status_code=502,
            detail=ErrorPayload(
                code=ErrorCode.UPSTREAM_ERROR, message="Company lookup failed"
            ).model_dump(),
        )

    # Clean the data and cache it
    payload = dict(data)
    payload.pop("x_cache", None)  # Remove cache info for clean response
    await cache_set(key, payload, TTL_COMPANY)
    return with_etag(request, payload, TTL_COMPANY)


@api_v1.get("/filings/{cvr}", response_model=models.FilingsResponse)
async def filings(cvr: str, limit: int = 10):
    prov = get_provider()
    data = await prov.list_filings(cvr, limit)
    return JSONResponse(data)


@api_v1.get(
    "/accounts/latest/{cvr}",
    response_model=models.AccountsResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60))],
)
async def latest_accounts(cvr: str):
    prov = get_provider()
    data = await prov.get_latest_accounts(cvr)
    return JSONResponse(data)


@api_v1.get("/compare/{cvr}", response_model=models.CompareResponse)
async def compare(cvr: str):
    prov = get_provider()
    try:
        data = await prov.get_latest_accounts(cvr)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    accounts_data = data.get("accounts") if data else None
    current_snapshot = None
    previous_snapshot = None

    if accounts_data and isinstance(accounts_data, dict):
        current_data = accounts_data.get("current")
        previous_data = accounts_data.get("previous")

        if current_data:
            current_snapshot = models.AccountsSnapshot(**current_data)
        if previous_data:
            previous_snapshot = models.AccountsSnapshot(**previous_data)

    # Use new comparison function
    comparison_result = compare_accounts_snapshots(current_snapshot, previous_snapshot)

    # Add original citations
    all_sources = comparison_result.get("sources", [])
    if data and data.get("citations"):
        all_sources.extend(data.get("citations", []))

    response_data = {
        "current_period": comparison_result.get("current_period"),
        "previous_period": comparison_result.get("previous_period"),
        "key_changes": [change.model_dump() for change in comparison_result.get("key_changes", [])],
        "narrative": comparison_result.get("narrative", "No comparison available."),
        "sources": all_sources,
    }

    return JSONResponse(response_data)


@api_v1.get("/compare/{cvr}/export")
async def export_comparison(cvr: str, format: str = "csv"):
    """Export comparison data as CSV or Excel."""
    prov = get_provider()
    try:
        data = await prov.get_latest_accounts(cvr)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    accounts_data = data.get("accounts") if data else None
    current_snapshot = None
    previous_snapshot = None

    if accounts_data and isinstance(accounts_data, dict):
        current_data = accounts_data.get("current")
        previous_data = accounts_data.get("previous")

        if current_data:
            current_snapshot = models.AccountsSnapshot(**current_data)
        if previous_data:
            previous_snapshot = models.AccountsSnapshot(**previous_data)

    comparison_result = compare_accounts_snapshots(current_snapshot, previous_snapshot)

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow(
        [
            "Field",
            f"{comparison_result.get('previous_period', 'Previous')} Value",
            f"{comparison_result.get('current_period', 'Current')} Value",
            "Absolute Change",
            "Percentage Change",
        ]
    )

    # Data rows
    for change in comparison_result.get("key_changes", []):
        writer.writerow(
            [
                change.field,
                f"{change.previous_value:,.0f}" if change.previous_value else "N/A",
                f"{change.current_value:,.0f}" if change.current_value else "N/A",
                f"{change.absolute_change:,.0f}" if change.absolute_change else "N/A",
                f"{change.percentage_change:.1f}%" if change.percentage_change else "N/A",
            ]
        )

    output.seek(0)

    return StreamingResponse(
        io.StringIO(output.getvalue()),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=company_{cvr}_comparison.csv"},
    )
