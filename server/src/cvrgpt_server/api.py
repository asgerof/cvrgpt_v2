from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .logging import setup_logging
from .providers.fixtures import FixtureProvider
from .providers.cvr_api import CVRApiProvider
from .services.compare import compare_accounts, narrate_compare
from .mcp_server import mcp

log = setup_logging()

def get_provider():
    if settings.provider == "fixtures":
        return FixtureProvider()
    elif settings.provider == "cvr_api":
        if not settings.api_base_url or not settings.api_key:
            raise RuntimeError("CVR API requires CVRGPT_API_BASE_URL + CVRGPT_API_KEY")
        return CVRApiProvider(settings.api_base_url, settings.api_key)
    else:
        raise RuntimeError(f"Unknown provider: {settings.provider}")

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

@app.get("/healthz")
async def health():
    return {"status": "ok", "provider": settings.provider}

@app.get("/v1/search")
async def search(q: str, limit: int = 10):
    prov = get_provider()
    data = await prov.search_companies(q, limit)
    return JSONResponse(data)

@app.get("/v1/company/{cvr}")
async def company(cvr: str):
    prov = get_provider()
    try:
        data = await prov.get_company(cvr)
    except FileNotFoundError:
        raise HTTPException(404, "Not found")
    return JSONResponse(data)

@app.get("/v1/filings/{cvr}")
async def filings(cvr: str, limit: int = 10):
    prov = get_provider()
    data = await prov.list_filings(cvr, limit)
    return JSONResponse(data)

@app.get("/v1/accounts/latest/{cvr}")
async def latest_accounts(cvr: str):
    prov = get_provider()
    data = await prov.get_latest_accounts(cvr)
    return JSONResponse(data)

@app.get("/v1/compare/{cvr}")
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
