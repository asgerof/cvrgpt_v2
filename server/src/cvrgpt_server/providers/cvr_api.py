from .base import Provider

class CVRApiProvider(Provider):
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    async def search_companies(self, q: str, limit: int = 10) -> dict:
        return {"items": [], "citations": [{"source": "cvr_api", "note": "not implemented"}]}

    async def get_company(self, cvr: str) -> dict:
        return {"company": None, "citations": [{"source": "cvr_api", "note": "not implemented"}]}

    async def list_filings(self, cvr: str, limit: int = 10) -> dict:
        return {"filings": [], "citations": [{"source": "cvr_api", "note": "not implemented"}]}

    async def get_latest_accounts(self, cvr: str) -> dict:
        return {"accounts": None, "citations": [{"source": "cvr_api", "note": "not implemented"}]}
