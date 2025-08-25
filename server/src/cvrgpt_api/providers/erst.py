import time
from typing import Any, Dict, Optional
from .base import Provider
import os
import httpx
from datetime import datetime


class ERSTProvider(Provider):
    """
    Concrete provider backed by ERST/Datafordeler.
    Replace HTTP calls with your internal client(s). Keep the method names
    aligned with the rest of the codebase so no higher-level changes are needed.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        auth_url: str,
        token_audience: str,
        api_base: str,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        basic_user: Optional[str] = None,
        basic_password: Optional[str] = None,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._auth_url = auth_url
        self._token_audience = token_audience
        self._api_base = api_base
        self._cert_path = cert_path
        self._key_path = key_path
        self._basic_user = basic_user
        self._basic_password = basic_password
        self._token = None
        self._token_exp = 0

    # --- auth/token management (stub; swap for your real implementation) ---
    def _ensure_token(self):
        now = int(time.time())
        if self._token and now < self._token_exp - 60:
            return
        if not self._auth_url:
            # Basic auth mode – no token to fetch
            return
        # OAuth2 Client Credentials (generic)
        # Expect auth_url to accept client_id, client_secret, audience/scope
        client_auth_in_body = os.getenv("ERST_CLIENT_AUTH_IN_BODY", "1") == "1"
        data = {
            "grant_type": "client_credentials",
        }
        if self._token_audience:
            # some providers use 'audience', others 'scope'
            data[os.getenv("ERST_TOKEN_AUDIENCE_FIELD", "audience")] = self._token_audience
        auth = None
        headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
        if not client_auth_in_body:
            auth = (self._client_id, self._client_secret)
        else:
            data["client_id"] = self._client_id
            data["client_secret"] = self._client_secret

        with httpx.Client(timeout=20.0) as client:
            r = client.post(self._auth_url, data=data, auth=auth, headers=headers)
        r.raise_for_status()
        payload = r.json()
        self._token = payload.get("access_token")
        ttl = int(payload.get("expires_in") or 3600)
        self._token_exp = now + min(ttl, 3600)

    def ping(self) -> bool:
        """
        Lightweight call to confirm credentials are accepted and the API is reachable.
        Implement with a cheap endpoint (e.g., /heartbeat or a tiny lookup).
        """
        try:
            if self._auth_url:
                self._ensure_token()
                return bool(self._token and self._api_base)
            # Basic auth mode: require base, user, password
            return bool(self._api_base and self._basic_user and self._basic_password)
        except Exception:
            return False

    # --- shape your public methods to match existing service contracts ---
    async def search_companies(self, q: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Search companies using CVR Permanent index (Elasticsearch _search)."""
        self._ensure_token()
        index_url = f"{self._api_base.rstrip('/')}/virksomhed/_search"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        auth = None
        if self._auth_url:
            headers["Authorization"] = f"Bearer {self._token}"
        elif self._basic_user and self._basic_password:
            auth = (self._basic_user, self._basic_password)
        cert = (self._cert_path, self._key_path) if self._cert_path and self._key_path else None

        is_cvr = q.isdigit() and len(q) == 8
        if is_cvr:
            query = {
                "query": {"bool": {"must": [{"term": {"Vrvirksomhed.cvrNummer": q}}]}},
                "from": max(int(offset), 0),
                "size": min(max(int(limit), 1), 25),
            }
        else:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match": {
                                    "Vrvirksomhed.virksomhedMetadata.nyesteNavn.navn": {
                                        "query": q,
                                        "operator": "and",
                                    }
                                }
                            }
                        ]
                    }
                },
                "from": max(int(offset), 0),
                "size": min(max(int(limit), 1), 25),
            }

        async with httpx.AsyncClient(timeout=30.0, cert=cert) as client:
            r = await client.post(
                index_url, headers=headers, auth=auth if auth else None, json=query
            )
        r.raise_for_status()
        payload = r.json()
        hits = (payload.get("hits") or {}).get("hits") or []

        def _map_item(hit: Dict[str, Any]) -> Dict[str, Any]:
            src = (hit.get("_source") or {}).get("Vrvirksomhed") or {}
            md = src.get("virksomhedMetadata") or {}
            navn = (md.get("nyesteNavn") or {}).get("navn")
            status = None
            vs = src.get("virksomhedsstatus") or {}
            # virksomhedsstatus may be nested list; try common shapes
            if isinstance(vs, dict):
                status = vs.get("status")
            city = (md.get("nyesteBeliggenhedsadresse") or {}).get("postdistrikt")
            hovedbranche = md.get("nyesteHovedbranche") or {}
            industry = {
                "code": hovedbranche.get("branchekode"),
                "text": hovedbranche.get("branchetekst"),
            }
            return {
                "cvr": src.get("cvrNummer"),
                "name": navn,
                "status": status,
                "city": city,
                "industry": industry,
            }

        items = [_map_item(h) for h in hits]
        total = ((payload.get("hits") or {}).get("total") or {}).get("value", len(items))
        return {
            "items": items,
            "total": total,
            "citations": [{"source": "erst", "url": index_url}],
        }

    async def get_company(self, cvr: str) -> Dict[str, Any]:
        self._ensure_token()
        index_url = f"{self._api_base.rstrip('/')}/virksomhed/_search"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        auth = None
        if self._auth_url:
            headers["Authorization"] = f"Bearer {self._token}"
        elif self._basic_user and self._basic_password:
            auth = (self._basic_user, self._basic_password)
        cert = (self._cert_path, self._key_path) if self._cert_path and self._key_path else None

        query = {
            "query": {"bool": {"must": [{"term": {"Vrvirksomhed.cvrNummer": str(cvr)}}]}},
            "size": 1,
        }

        async with httpx.AsyncClient(timeout=30.0, cert=cert) as client:
            r = await client.post(
                index_url, headers=headers, auth=auth if auth else None, json=query
            )
        r.raise_for_status()
        hits = (r.json().get("hits") or {}).get("hits") or []
        if not hits:
            raise FileNotFoundError(f"Company {cvr} not found")
        src = (hits[0].get("_source") or {}).get("Vrvirksomhed") or {}
        md = src.get("virksomhedMetadata") or {}

        company = {
            "cvr": src.get("cvrNummer") or cvr,
            "name": (md.get("nyesteNavn") or {}).get("navn") or f"Company {cvr}",
            "status": ((src.get("virksomhedsstatus") or {}) or {}).get("status"),
            "city": ((md.get("nyesteBeliggenhedsadresse") or {}) or {}).get("postdistrikt"),
            "industry": {
                "code": (md.get("nyesteHovedbranche") or {}).get("branchekode"),
                "text": (md.get("nyesteHovedbranche") or {}).get("branchetekst"),
            },
            "last_accounts_year": None,
            "addresses": [md.get("nyesteBeliggenhedsadresse")],
        }

        return {"company": company, "citations": [{"source": "erst", "url": index_url}]}

    async def list_filings(self, cvr: str, limit: int = 10) -> Dict[str, Any]:
        self._ensure_token()
        url = f"{self._api_base.rstrip('/')}/companies/{cvr}/filings"
        headers: Dict[str, str] = {}
        auth = None
        if self._auth_url:
            headers["Authorization"] = f"Bearer {self._token}"
        elif self._basic_user and self._basic_password:
            auth = (self._basic_user, self._basic_password)
        params = {"limit": limit}
        cert = (self._cert_path, self._key_path) if self._cert_path and self._key_path else None
        async with httpx.AsyncClient(timeout=30.0, cert=cert) as client:
            r = await client.get(url, headers=headers, params=params, auth=auth)
        r.raise_for_status()
        data = r.json()
        filings = []
        for f in data.get("items", data if isinstance(data, list) else []):
            filings.append(
                {
                    "id": f.get("id") or f.get("document_id"),
                    "type": f.get("type") or f.get("document_type"),
                    "date": (f.get("date") or f.get("published_at") or ""),
                }
            )
        return {"filings": filings[:limit], "citations": [{"source": "erst", "url": url}]}

    async def get_latest_accounts(self, cvr: str) -> Dict[str, Any]:
        self._ensure_token()
        url = f"{self._api_base.rstrip('/')}/companies/{cvr}/accounts/latest"
        headers: Dict[str, str] = {}
        auth = None
        if self._auth_url:
            headers["Authorization"] = f"Bearer {self._token}"
        elif self._basic_user and self._basic_password:
            auth = (self._basic_user, self._basic_password)
        cert = (self._cert_path, self._key_path) if self._cert_path and self._key_path else None
        async with httpx.AsyncClient(timeout=30.0, cert=cert) as client:
            r = await client.get(url, headers=headers, auth=auth)
        r.raise_for_status()
        data = r.json()

        # Normalize fields commonly used by compare and tools
        def _to_period(d: Dict[str, Any] | None) -> Dict[str, Any] | None:
            if not d:
                return None
            period = d.get("period") or {}
            year = (
                period.get("year")
                or period.get("end_year")
                or (
                    datetime.fromisoformat(period.get("end")).date()
                    if isinstance(period.get("end"), str) and period.get("end")
                    else None
                )
            )
            if isinstance(year, datetime):
                year = year.year
            return {
                "period": {"year": year},
                "revenue": d.get("revenue"),
                "ebit": d.get("ebit"),
                "net_income": d.get("net_income"),
                "equity": d.get("equity"),
                "employees": d.get("employees"),
            }

        accounts = {
            "current": _to_period(data.get("current")),
            "previous": _to_period(data.get("previous")),
        }
        return {"accounts": accounts, "citations": [{"source": "erst", "url": url}]}
