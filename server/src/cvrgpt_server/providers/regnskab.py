from .base import Provider
from typing import Dict, Any, List


class RegnskabProvider(Provider):
    """Placeholder provider for filings and accounts from Regnskabsdata/Offentliggørelser.
    Implement actual HTTP calls when endpoints are confirmed.
    """

    async def search_companies(self, q: str, limit: int = 10) -> dict:
        # Not responsible for search; return empty
        return {"items": [], "citations": []}

    async def get_company(self, cvr: str) -> dict:
        # Not responsible for profile; return empty
        return {"company": None, "citations": []}

    async def list_filings(self, cvr: str, limit: int = 10) -> dict:
        # TODO: call Regnskabsdata listings
        return {"filings": [], "citations": []}

    async def get_latest_accounts(self, cvr: str) -> dict:
        # TODO: parse iXBRL/PDF to 6 facts
        return {"accounts": None, "citations": []}


