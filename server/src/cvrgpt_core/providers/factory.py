import os
from typing import Protocol, Any, Dict

class Provider(Protocol):
    def ping(self) -> bool: ...
    async def search_companies(self, q: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]: ...
    async def get_company(self, cvr: str) -> Dict[str, Any]: ...
    async def list_filings(self, cvr: str, limit: int = 10) -> Dict[str, Any]: ...
    async def get_latest_accounts(self, cvr: str) -> Dict[str, Any]: ...

_provider_singleton: Provider | None = None

def _app_env() -> str:
    return os.getenv("APP_ENV", "dev").lower()

def _provider_name() -> str:
    return os.getenv("DATA_PROVIDER", "erst").lower()

def get_provider() -> Provider:
    global _provider_singleton
    if _provider_singleton:
        return _provider_singleton

    name = _provider_name()
    env = _app_env()

    if name == "erst":
        # Import ERST provider only when needed to avoid circular imports
        from cvrgpt_api.providers.erst import ERSTProvider
        
        missing = [k for k in [
            "ERST_CLIENT_ID", "ERST_CLIENT_SECRET", "ERST_AUTH_URL",
            "ERST_TOKEN_AUDIENCE", "ERST_API_BASE_URL"
        ] if not os.getenv(k)]
        if missing and env != "dev":
            raise RuntimeError(
                f"ERST provider selected but required env vars are missing: {', '.join(missing)}"
            )
        _provider_singleton = ERSTProvider(
            client_id=os.getenv("ERST_CLIENT_ID", ""),
            client_secret=os.getenv("ERST_CLIENT_SECRET", ""),
            auth_url=os.getenv("ERST_AUTH_URL", ""),
            token_audience=os.getenv("ERST_TOKEN_AUDIENCE", ""),
            api_base=os.getenv("ERST_API_BASE_URL", ""),
            cert_path=os.getenv("ERST_CERT_PATH"),
            key_path=os.getenv("ERST_KEY_PATH"),
        )
        return _provider_singleton

    if name == "fixture":
        # Import fixture provider only when needed to avoid circular imports
        from cvrgpt_api.providers.fixtures import FixtureProvider
        from cvrgpt_api.providers.base import CompositeProvider
        
        fixture_provider = FixtureProvider()
        _provider_singleton = CompositeProvider(
            core=fixture_provider, filings_provider=fixture_provider
        )
        return _provider_singleton

    raise RuntimeError(f"Unknown DATA_PROVIDER '{name}'. Use 'erst' or 'fixture'.")
