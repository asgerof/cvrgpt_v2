import os
from cvrgpt_core.providers.fixture import FixtureProvider
from cvrgpt_core.providers.base import Provider

def get_provider() -> Provider:
    provider_type = os.getenv("PROVIDER", "fixture")
    if provider_type == "fixture":
        return FixtureProvider()
    else:
        # TODO: Add other providers (CVR API, etc.)
        return FixtureProvider()
