from typing import Optional, Dict, Any, List
from ..models import AccountsSnapshot, AccountsDelta
import datetime


def compare_accounts_snapshots(current: Optional[AccountsSnapshot], previous: Optional[AccountsSnapshot]) -> Dict[str, Any]:
    """Compare two AccountsSnapshot objects and return key changes with narrative."""
    if not current or not previous:
        return {
            "current_period": getattr(current.period, "year", None) if current and current.period else None,
            "previous_period": getattr(previous.period, "year", None) if previous and previous.period else None,
            "key_changes": [],
            "narrative": "Insufficient data for comparison.",
            "sources": []
        }
    
    # Key fields to compare
    fields = [
        ("revenue", "Revenue"),
        ("ebit", "EBIT"),
        ("net_income", "Net Income"),
        ("assets", "Total Assets"),
        ("equity", "Equity"),
        ("cash", "Cash")
    ]
    
    key_changes: List[AccountsDelta] = []
    
    for field_key, field_label in fields:
        curr_val = getattr(current, field_key, None)
        prev_val = getattr(previous, field_key, None)
        
        if curr_val is not None and prev_val is not None and prev_val != 0:
            abs_change = curr_val - prev_val
            pct_change = (abs_change / abs(prev_val)) * 100
            
            key_changes.append(AccountsDelta(
                field=field_label,
                current_value=curr_val,
                previous_value=prev_val,
                absolute_change=abs_change,
                percentage_change=pct_change
            ))
    
    # Sort by absolute percentage change (descending)
    key_changes.sort(key=lambda x: abs(x.percentage_change or 0), reverse=True)
    
    # Generate narrative
    narrative_parts = []
    curr_period = str(current.period.year) if current.period and current.period.year else "current"
    prev_period = str(previous.period.year) if previous.period and previous.period.year else "previous"
    
    if key_changes:
        top_changes = key_changes[:3]  # Top 3 changes
        for change in top_changes:
            if change.percentage_change and abs(change.percentage_change) > 1:  # Only mention >1% changes
                direction = "increased" if change.percentage_change > 0 else "decreased"
                narrative_parts.append(
                    f"{change.field} {direction} {abs(change.percentage_change):.1f}% "
                    f"({format_currency(change.previous_value)} → {format_currency(change.current_value)})"
                )
    
    narrative = f"Comparing {prev_period} to {curr_period}: " + "; ".join(narrative_parts) if narrative_parts else "No significant changes detected."
    
    # Collect all source anchors
    sources = []
    if current and current.source_anchors:
        sources.extend(current.source_anchors)
    if previous and previous.source_anchors:
        sources.extend(previous.source_anchors)
    
    return {
        "current_period": curr_period,
        "previous_period": prev_period,
        "key_changes": key_changes,
        "narrative": narrative,
        "sources": sources
    }


def format_currency(value: Optional[float]) -> str:
    """Format currency values in millions/thousands."""
    if value is None:
        return "n/a"
    
    if abs(value) >= 1_000_000:
        return f"{value/1_000_000:.1f}M DKK"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.0f}K DKK"
    else:
        return f"{value:.0f} DKK"


# Legacy functions for backward compatibility
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
