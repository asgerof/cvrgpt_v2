from typing import Dict, Optional
from ..models import Accounts, CompareAccountsResponse, Citation

NUM_FIELDS = ("revenue", "ebit", "equity")

def _delta(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None: return None
    return a - b

def compare(a: Accounts, b: Accounts) -> CompareAccountsResponse:
    deltas: Dict[str, Optional[float]] = {k: _delta(getattr(a, k), getattr(b, k)) for k in NUM_FIELDS}
    merged_citations = (a.citations or []) + (b.citations or [])
    return CompareAccountsResponse(a=a, b=b, deltas=deltas, citations=merged_citations)
