import os
from cvrgpt_core.providers.fixture import FixtureProvider
from cvrgpt_core.providers.base import Provider


def get_provider() -> Provider:
    name = (os.getenv("CVRGPT_PROVIDER") or "fixture").lower()
    if name == "fixture":
        return FixtureProvider()
    # add real providers here later
    return FixtureProvider()
