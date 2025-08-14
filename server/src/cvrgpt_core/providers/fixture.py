from typing import List
from .base import Provider
from ..models import Company, Filing, Accounts, Citation

class FixtureProvider(Provider):
    def search_companies(self, q: str) -> List[Company]:
        # TODO: map from existing fixture store
        return [Company(cvr="12345678", name="Demo A/S")]

    def get_company(self, cvr: str) -> Company:
        return Company(cvr=cvr, name="Demo A/S", address="Some Street 1, 1000 København")

    def list_filings(self, cvr: str) -> List[Filing]:
        return [Filing(id="fil-2024", year=2024, type="annual_report")]

    def latest_accounts(self, cvr: str) -> Accounts:
        from pydantic import HttpUrl
        return Accounts(year=2024, revenue=1000000.0, ebit=120000.0, equity=500000.0,
                        citations=[Citation(url=HttpUrl("https://example.com/fixture"))])
