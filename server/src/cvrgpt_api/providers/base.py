from abc import ABC, abstractmethod


class Provider(ABC):
    @abstractmethod
    async def search_companies(self, q: str, limit: int = 10, offset: int = 0) -> dict: ...
    @abstractmethod
    async def get_company(self, cvr: str) -> dict: ...
    @abstractmethod
    async def list_filings(self, cvr: str, limit: int = 10) -> dict: ...
    @abstractmethod
    async def get_latest_accounts(self, cvr: str) -> dict: ...
    
    def ping(self) -> bool:
        """Health check method. Override in concrete providers."""
        return True


class CompositeProvider(Provider):
    def __init__(self, core: Provider, filings_provider: Provider | None = None):
        self.core = core
        self.filings_provider = filings_provider or core

    async def search_companies(self, q: str, limit: int = 10, offset: int = 0) -> dict:
        return await self.core.search_companies(q, limit, offset)

    async def get_company(self, cvr: str) -> dict:
        return await self.core.get_company(cvr)

    async def list_filings(self, cvr: str, limit: int = 10) -> dict:
        return await self.filings_provider.list_filings(cvr, limit)

    async def get_latest_accounts(self, cvr: str) -> dict:
        return await self.filings_provider.get_latest_accounts(cvr)
    
    def ping(self) -> bool:
        """Health check - both core and filings providers must be healthy."""
        return self.core.ping() and self.filings_provider.ping()
