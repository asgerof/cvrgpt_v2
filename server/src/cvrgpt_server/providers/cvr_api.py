from .base import Provider
import httpx
from cachetools import TTLCache
from typing import Any, Dict
from urllib.parse import urlencode

class CVRApiProvider(Provider):
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        # very small in-memory cache
        self._cache = TTLCache(maxsize=512, ttl=600)
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(5.0, read=5.0, connect=5.0))

    async def search_companies(self, q: str, limit: int = 10) -> dict:
        key = ("search", q, limit)
        if key in self._cache:
            data = self._cache[key]
            data["x_cache"] = "hit"
            return data
        params = {"q": q, "limit": limit}
        url = f"{self.base_url}/search?{urlencode(params)}"
        headers = {"Authorization": f"Bearer {self.token}"}
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
        headers = {"Authorization": f"Bearer {self.token}"}
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
        return {"filings": [], "citations": [{"source": "cvr_api", "note": "not implemented"}]}

    async def get_latest_accounts(self, cvr: str) -> dict:
        return {"accounts": None, "citations": [{"source": "cvr_api", "note": "not implemented"}]}
