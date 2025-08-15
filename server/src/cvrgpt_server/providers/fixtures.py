import json
import pathlib
from .base import Provider

FIX = pathlib.Path(__file__).parents[1] / "fixtures"


class FixtureProvider(Provider):
    async def search_companies(self, q: str, limit: int = 10) -> dict:
        items = []
        for p in (FIX / "companies").glob("*.json"):
            data = json.loads(p.read_text(encoding="utf-8"))
            name = data.get("name", "")
            if q.lower() in name.lower() or q in data.get("cvr", ""):
                items.append(
                    {"cvr": data["cvr"], "name": data["name"], "status": data.get("status", "")}
                )
        return {"items": items[:limit], "citations": [{"source": "fixtures"}]}

    async def get_company(self, cvr: str) -> dict:
        p = FIX / "companies" / f"{cvr}.json"
        if not p.exists():
            raise FileNotFoundError(f"No fixture for {cvr}")
        data = json.loads(p.read_text(encoding="utf-8"))
        return {"company": data, "citations": [{"source": "fixtures", "path": str(p)}]}

    async def list_filings(self, cvr: str, limit: int = 10) -> dict:
        p = FIX / "filings" / f"{cvr}.json"
        items = []
        if p.exists():
            items = json.loads(p.read_text(encoding="utf-8")).get("filings", [])
        return {"filings": items[:limit], "citations": [{"source": "fixtures", "path": str(p)}]}

    async def get_latest_accounts(self, cvr: str) -> dict:
        p = FIX / "filings" / f"{cvr}.json"
        if not p.exists():
            return {"accounts": None, "citations": [{"source": "fixtures"}]}
        data = json.loads(p.read_text(encoding="utf-8"))
        acc = data.get("latest_accounts")
        return {"accounts": acc, "citations": [{"source": "fixtures", "path": str(p)}]}
