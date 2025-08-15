from mcp.server.fastmcp import FastMCP
from .providers.fixtures import FixtureProvider
from .providers.cvr_api import CVRApiProvider
from .services.compare import compare_accounts, narrate_compare
from .config import settings

mcp = FastMCP("CVRGPT")


def get_provider():
    if settings.provider == "fixtures":
        return FixtureProvider()
    elif settings.provider == "cvr_api":
        return CVRApiProvider(settings.api_base_url or "", settings.api_key or "")
    else:
        return FixtureProvider()


@mcp.tool()
async def search_companies(q: str, limit: int = 10) -> dict:
    "Search companies by name or CVR number. Returns items and citations."
    prov = get_provider()
    return await prov.search_companies(q, limit)


@mcp.tool()
async def get_company(cvr: str) -> dict:
    "Get a detailed company profile by CVR."
    prov = get_provider()
    return await prov.get_company(cvr)


@mcp.tool()
async def list_filings(cvr: str, limit: int = 10) -> dict:
    "List public filings (e.g., annual reports)."
    prov = get_provider()
    return await prov.list_filings(cvr, limit)


@mcp.tool()
async def get_latest_accounts(cvr: str) -> dict:
    "Get latest accounts (normalized summary) with previous period if available."
    prov = get_provider()
    return await prov.get_latest_accounts(cvr)


@mcp.tool()
async def compare_accounts_tool(cvr: str) -> dict:
    "Compute ratios & deltas between the last two account periods with citations and a short narrative."
    prov = get_provider()
    data = await prov.get_latest_accounts(cvr)
    latest = data.get("accounts")
    if not latest or not latest.get("previous"):
        return {
            "comparison": None,
            "narrative": "No comparable accounts available.",
            "citations": data.get("citations", []),
        }
    comp = compare_accounts(latest.get("previous"), latest.get("current"))
    narrative = narrate_compare(comp)
    return {"comparison": comp, "narrative": narrative, "citations": data.get("citations", [])}


if __name__ == "__main__":
    import sys
    import asyncio

    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    if mode == "stdio":
        asyncio.run(mcp.run_stdio_async())
    elif mode == "sse":
        import uvicorn
        from fastapi import FastAPI

        app = FastAPI()
        app.mount("/", mcp.sse_app())
        uvicorn.run(app, host="0.0.0.0", port=8765)
    else:
        print("Usage: python -m cvrgpt_server.mcp_server [stdio|sse]")
