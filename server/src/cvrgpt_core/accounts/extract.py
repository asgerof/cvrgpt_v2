from typing import Optional, Dict, Any
from .extract_real import get_annual_result_real

def get_annual_result(company_query: str, year: int) -> Optional[Dict[str, Any]]:
    """
    Try real extraction first, fallback to fixture data.
    """
    real = get_annual_result_real(company_query, year)
    if real:
        return real
    # fallback to fixture
    from .fixtures import annual_results
    key = (company_query.lower().strip(), year)
    return annual_results.get(key)
