from typing import Optional, Dict, Any

def get_annual_result(company_query: str, year: int) -> Optional[Dict[str, Any]]:
    """
    TEMP: reads from a small fixture mapping { (normalized_name, year): result }.
    Replace with real iXBRL/pdf extraction later.
    """
    norm = company_query.lower().strip()
    from .fixtures import annual_results  # small dict
    key = (norm, year)
    return annual_results.get(key)
