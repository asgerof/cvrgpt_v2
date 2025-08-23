import os
REAL = os.getenv("ACCOUNTS_REAL", "0") == "1"

def get_annual_result_real(company_query: str, year: int):
    if not REAL:
        return None
    # TODO:
    # 1) resolve company to CVR
    # 2) fetch filing for the year
    # 3) parse iXBRL (preferred) or PDF fallback
    # 4) extract Årets resultat numeric and currency
    return None
