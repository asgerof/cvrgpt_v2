from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .logging import setup_logging
from .providers.fixtures import FixtureProvider
from .providers.cvr_api import CVRApiProvider
from .providers.regnskab import RegnskabProvider
from .providers.base import CompositeProvider
from .services.compare import compare_accounts, narrate_compare
from .mcp_server import mcp
from . import models
from .errors import ErrorPayload
import uuid

log = setup_logging()

_provider_instance = None

def get_provider():
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance
    if settings.provider == "fixtures":
        _provider_instance = FixtureProvider()
    elif settings.provider == "cvr_api":
        if not settings.api_base_url:
            raise RuntimeError("CVR API requires CVRGPT_API_BASE_URL")
        core = CVRApiProvider(settings.api_base_url, settings.api_key, settings.api_user, settings.api_password)
        filings = RegnskabProvider()
        _provider_instance = CompositeProvider(core=core, filings_provider=filings)
    else:
        raise RuntimeError(f"Unknown provider: {settings.provider}")
    return _provider_instance

app = FastAPI(title="CVRGPT Server", version="0.1.0")

# Wire up metrics
from cvrgpt_server import metrics
app.middleware("http")(metrics.timing_middleware)
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

@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = req_id
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize error payloads
    code = "BAD_REQUEST" if exc.status_code == 400 else (
        "NOT_FOUND" if exc.status_code == 404 else (
        "UPSTREAM_ERROR" if exc.status_code == 502 else "ERROR"))
    detail = None
    if isinstance(exc.detail, dict) and exc.detail.get("detail"):
        detail = exc.detail.get("detail")
    elif isinstance(exc.detail, str):
        detail = exc.detail
    payload = ErrorPayload(code=code, detail=detail).model_dump()
    return JSONResponse(status_code=exc.status_code, content=payload)

@app.get("/healthz", response_model=dict)
async def health():
    return {"status": "ok", "provider": settings.provider}

@app.get("/v1/search", response_model=models.SearchResponse)
async def search(q: str, limit: int = 10, response: Response = None):
    prov = get_provider()
    try:
        data = await prov.search_companies(q, limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    x_cache = data.pop("x_cache", None)
    if response is not None and x_cache:
        response.headers["X-Cache"] = x_cache
    return JSONResponse(data)

@app.get("/v1/company/{cvr}", response_model=models.CompanyResponse)
async def company(cvr: str, response: Response = None):
    prov = get_provider()
    try:
        data = await prov.get_company(cvr)
    except FileNotFoundError:
        raise HTTPException(404, "Not found")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    x_cache = data.pop("x_cache", None)
    if response is not None and x_cache:
        response.headers["X-Cache"] = x_cache
    return JSONResponse(data)

@app.get("/v1/filings/{cvr}", response_model=models.FilingsResponse)
async def filings(cvr: str, limit: int = 10):
    prov = get_provider()
    data = await prov.list_filings(cvr, limit)
    return JSONResponse(data)

@app.get("/v1/accounts/latest/{cvr}", response_model=models.AccountsResponse)
async def latest_accounts(cvr: str):
    prov = get_provider()
    data = await prov.get_latest_accounts(cvr)
    return JSONResponse(data)

@app.get("/v1/compare/{cvr}", response_model=models.CompareResponse)
async def compare(cvr: str):
    prov = get_provider()
    data = await prov.get_latest_accounts(cvr)
    latest = data.get("accounts")
    if not latest or not latest.get("previous"):
        return JSONResponse({
            "comparison": None,
            "narrative": "No comparable accounts available.",
            "citations": data.get("citations", [])
        })
    comp = compare_accounts(latest.get("previous"), latest.get("current"))
    narrative = narrate_compare(comp)
    citations = data.get("citations", [])
    return JSONResponse({"comparison": comp, "narrative": narrative, "citations": citations})
