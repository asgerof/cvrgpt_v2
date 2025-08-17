from fastapi import APIRouter
from cvrgpt_core.providers.factory import get_provider, _provider_name

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/provider")
def provider_health():
    """Check provider health and return status"""
    prov = get_provider()
    ok = False
    try:
        ok = bool(getattr(prov, "ping", lambda: False)())
    except Exception:
        ok = False
    return {
        "provider": _provider_name(),
        "ok": ok
    }
