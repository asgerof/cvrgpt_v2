from .base import Provider
import httpx
from cachetools import TTLCache
from typing import Any, Dict, List
from urllib.parse import urlencode

class CVRApiProvider(Provider):
    def __init__(self, base_url: str, token: str | None = None, user: str | None = None, password: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.user = user
        self.password = password
        # very small in-memory cache
        self._cache = TTLCache(maxsize=512, ttl=600)
        auth = None
        if self.user and self.password:
            auth = httpx.BasicAuth(self.user, self.password)
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=5.0, connect=5.0), auth=auth)

    async def search_companies(self, q: str, limit: int = 10) -> dict:
        key = ("search", q, limit)
        if key in self._cache:
            data = self._cache[key]
            data["x_cache"] = "hit"
            return data
        params = {"q": q, "limit": limit}
        url = f"{self.base_url}/search?{urlencode(params)}"
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            r = await self._client.get(url, headers=headers)
            r.raise_for_status()
            payload = r.json()
            items = [
                {
                    "cvr": str(it.get("cvr") or it.get("id") or ""),
                    "name": it.get("name") or it.get("company_name") or "",
                    "status": it.get("status"),
                }
                for it in payload.get("items", [])
            ][:limit]
            data = {"items": items, "citations": [{"source": "api", "url": url}]}
            self._cache[key] = data
            data_out = dict(data)
            data_out["x_cache"] = "miss"
            return data_out
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(f"Upstream search failed: {e.response.text}", request=e.request, response=e.response)
        except Exception as e:
            # Let the API layer translate this into 502
            raise RuntimeError(f"search_companies failed: {e}")

    async def get_company(self, cvr: str) -> dict:
        key = ("company", cvr)
        if key in self._cache:
            data = self._cache[key]
            data["x_cache"] = "hit"
            return data
        url = f"{self.base_url}/company/{cvr}"
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            r = await self._client.get(url, headers=headers)
            if r.status_code == 404:
                raise FileNotFoundError(f"Company {cvr} not found")
            r.raise_for_status()
            src = r.json() or {}
            company = {
                "cvr": str(src.get("cvr") or src.get("id") or cvr),
                "name": src.get("name") or src.get("company_name") or "",
                "status": src.get("status"),
                "industry": {
                    "code": (src.get("industry") or {}).get("code") if isinstance(src.get("industry"), dict) else src.get("industry_code"),
                    "text": (src.get("industry") or {}).get("text") if isinstance(src.get("industry"), dict) else src.get("industry_text"),
                },
                "addresses": src.get("addresses") or [],
                "officers": src.get("officers") or [],
            }
            data = {"company": company, "citations": [{"source": "api", "url": url}]}
            self._cache[key] = data
            data_out = dict(data)
            data_out["x_cache"] = "miss"
            return data_out
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(f"Upstream company failed: {e.response.text}", request=e.request, response=e.response)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"get_company failed: {e}")

    async def list_filings(self, cvr: str, limit: int = 10) -> dict:
        key = ("filings", cvr, limit)
        if key in self._cache:
            data = self._cache[key]
            data["x_cache"] = "hit"
            return data
        params = {"limit": limit}
        url = f"{self.base_url}/filings/{cvr}?{urlencode(params)}"
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            r = await self._client.get(url, headers=headers)
            if r.status_code == 404:
                data = {"filings": [], "citations": [{"source": "api", "url": url}]}
                self._cache[key] = data
                out = dict(data); out["x_cache"] = "miss"; return out
            r.raise_for_status()
            payload = r.json() or {}
            filings_src: List[Dict[str, Any]] = payload.get("filings") or payload.get("items") or []
            filings = [
                {
                    "id": str(it.get("id") or it.get("identifier") or i),
                    "type": it.get("type") or it.get("document_type") or "annual_report",
                    "date": it.get("date") or it.get("published_at") or "",
                    "url": it.get("url") or it.get("link") or "",
                }
                for i, it in enumerate(filings_src)
            ][:limit]
            data = {"filings": filings, "citations": [{"source": "api", "url": url}]}
            self._cache[key] = data
            out = dict(data); out["x_cache"] = "miss"; return out
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(f"Upstream filings failed: {e.response.text}", request=e.request, response=e.response)
        except Exception as e:
            # return empty but cite attempted URL
            return {"filings": [], "citations": [{"source": "api", "url": url, "note": str(e)}]}

    async def get_latest_accounts(self, cvr: str) -> dict:
        # Try a canonical endpoint returning normalized accounts
        tried: List[str] = []
        headers: Dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        # 1) Attempt /accounts/latest/{cvr}
        url1 = f"{self.base_url}/accounts/latest/{cvr}"
        tried.append(url1)
        try:
            r1 = await self._client.get(url1, headers=headers)
            if r1.status_code == 200:
                payload = r1.json() or {}
                accounts = payload.get("accounts") or payload
                if isinstance(accounts, dict) and (accounts.get("current") or accounts.get("previous")):
                    return {"accounts": accounts, "citations": [{"source": "api", "url": url1}]}
        except Exception:
            pass
        # 2) Fallback: compute from minimal facts endpoint if present
        url2 = f"{self.base_url}/facts/summary/{cvr}"
        tried.append(url2)
        try:
            r2 = await self._client.get(url2, headers=headers)
            if r2.status_code == 200:
                fx = r2.json() or {}
                def build_period(src: Dict[str, Any]) -> Dict[str, Any]:
                    if not src: return {}
                    return {
                        "period": {"year": src.get("year")},
                        "pl": {
                            "revenue": src.get("Revenue"),
                            "ebit": src.get("EBIT"),
                        },
                        "bs": {
                            "assets": src.get("Assets"),
                            "equity": src.get("Equity"),
                            "current_assets": src.get("CurrentAssets"),
                            "current_liabilities": src.get("CurrentLiabilities"),
                        },
                        "citations": [{"type": "ixbrl", "url": src.get("source_url")}] if src.get("source_url") else [],
                    }
                accounts = {
                    "current": build_period(fx.get("current") or {}),
                    "previous": build_period(fx.get("previous") or {}),
                }
                return {"accounts": accounts, "citations": [{"source": "api", "url": url2}]}
        except Exception:
            pass
        # If nothing worked, return None with citations of attempted URLs
        return {"accounts": None, "citations": [{"source": "api", "url": u} for u in tried]}
