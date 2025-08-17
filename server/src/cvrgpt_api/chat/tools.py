from typing import List, Dict, Any
from decimal import Decimal
from ..api import get_provider


def _s(v):
    """stringify Decimals safely"""
    return str(v) if isinstance(v, Decimal) else ("" if v is None else str(v))


async def tool_search_company(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for companies by name or CVR"""
    provider = get_provider()
    result = await provider.search_companies(query, limit=min(max(limit, 1), 25))
    return result.get("items", [])


async def tool_get_company(cvr: str) -> Dict[str, Any]:
    """Get company details by CVR"""
    provider = get_provider()
    result = await provider.get_company(cvr)
    return result.get("company", {})


async def tool_get_financials(
    cvr: str, years: List[int] | None, metrics: List[str] | None
) -> Dict[str, Any]:
    """Get financial data for a company"""
    provider = get_provider()
    try:
        result = await provider.get_latest_accounts(cvr)
        accounts_data = result.get("accounts", {})

        if not accounts_data:
            return {
                "years": [],
                "revenue": {},
                "ebit": {},
                "ebitda": {},
                "net_income": {},
                "equity": {},
                "employees": {},
            }

        # Extract financial data from current and previous periods
        financials: Dict[str, Any] = {
            "years": [],
            "revenue": {},
            "ebit": {},
            "ebitda": {},
            "net_income": {},
            "equity": {},
            "employees": {},
        }

        for period_key in ["current", "previous"]:
            period_data = accounts_data.get(period_key)
            if period_data and period_data.get("period"):
                year = period_data["period"].get("year")
                if year and (not years or year in years):
                    financials["years"].append(year)

                    # Map financial metrics
                    financials["revenue"][str(year)] = _s(period_data.get("revenue"))
                    financials["ebit"][str(year)] = _s(period_data.get("ebit"))
                    financials["ebitda"][str(year)] = _s(
                        period_data.get("ebit")
                    )  # Using EBIT as EBITDA fallback
                    financials["net_income"][str(year)] = _s(period_data.get("net_income"))
                    financials["equity"][str(year)] = _s(period_data.get("equity"))
                    financials["employees"][str(year)] = _s(period_data.get("employees", "—"))

        financials["years"] = sorted(set(financials["years"]))
        return financials

    except Exception:
        # Return empty structure if no financial data available
        return {
            "years": [],
            "revenue": {},
            "ebit": {},
            "ebitda": {},
            "net_income": {},
            "equity": {},
            "employees": {},
        }


async def tool_list_filings(cvr: str, limit: int = 5) -> List[Dict[str, Any]]:
    """List filings for a company"""
    provider = get_provider()
    result = await provider.list_filings(cvr, limit=min(max(limit, 1), 50))
    filings = result.get("filings", [])

    # Normalize filing data structure
    normalized_filings = []
    for filing in filings:
        normalized_filings.append(
            {
                "date": filing.get("date", ""),
                "type": filing.get("type", ""),
                "id": filing.get("id", ""),
            }
        )

    return normalized_filings
