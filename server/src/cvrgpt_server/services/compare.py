from typing import Optional, Dict, Any

def compute_ratios(accounts: Dict[str, Any]) -> Dict[str, Optional[float]]:
    if not accounts:
        return {"margin": None, "solvency": None, "liquidity": None}
    pl, bs = accounts.get("pl", {}), accounts.get("bs", {})
    revenue = pl.get("revenue") or 0.0
    ebit = pl.get("ebit") or 0.0
    assets = bs.get("assets") or 0.0
    equity = bs.get("equity") or 0.0
    ca = bs.get("current_assets") or 0.0
    cl = bs.get("current_liabilities") or 0.0
    margin = (ebit / revenue) if revenue else None
    solvency = (equity / assets) if assets else None
    liquidity = (ca / cl) if cl else None
    return {"margin": margin, "solvency": solvency, "liquidity": liquidity}

def compare_accounts(prev: Dict[str, Any], curr: Dict[str, Any]) -> Dict[str, Any]:
    r_prev = compute_ratios(prev)
    r_curr = compute_ratios(curr)
    deltas = {}
    for k in ["margin", "solvency", "liquidity"]:
        a, b = r_prev.get(k), r_curr.get(k)
        deltas[k] = None if (a is None or b is None) else (b - a)
    return {"current": r_curr, "previous": r_prev, "delta": deltas}

def narrate_compare(comp: Dict[str, Any]) -> str:
    """Return a short, human-friendly narrative from compare_accounts output."""
    if not comp or not comp.get("current"):
        return "No comparable accounts available."
    curr, delta = comp.get("current", {}), comp.get("delta", {})
    def fmt_ratio(v: Optional[float]) -> str:
        if v is None: return "n/a"
        return f"{v:.2f}"
    def fmt_pct(v: Optional[float]) -> str:
        if v is None: return "n/a"
        return f"{v:.2%}"
    parts = []
    parts.append(f"Margin {fmt_pct(curr.get('margin'))} ({('+' if (delta.get('margin') or 0)>=0 else '')}{fmt_pct(delta.get('margin'))} YoY)")
    parts.append(f"Solvency {fmt_pct(curr.get('solvency'))} ({('+' if (delta.get('solvency') or 0)>=0 else '')}{fmt_pct(delta.get('solvency'))} YoY)")
    parts.append(f"Liquidity {fmt_ratio(curr.get('liquidity'))} ({('+' if (delta.get('liquidity') or 0)>=0 else '')}{fmt_ratio(delta.get('liquidity'))} YoY)")
    return "; ".join(parts) + "."
