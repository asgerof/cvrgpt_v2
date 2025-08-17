import re
from typing import List, Union
from .schemas import (
    ChatRequest,
    ChatResponse,
    TextBlock,
    CardBlock,
    TableBlock,
    ChoiceBlock,
    ChoiceItem,
)
from .state import get_or_create_thread, get_ctx, set_ctx, set_last_table
from .tools import tool_search_company, tool_get_company, tool_get_financials, tool_list_filings

CVR_RE = re.compile(r"\b(\d{8})\b")  # DK CVR is 8 digits


def _parse_years(text: str) -> List[int]:
    years = [int(y) for y in re.findall(r"\b(20\d{2}|19\d{2})\b", text)]
    return sorted(set(years))[-5:]


def _intent(text: str) -> str:
    t = text.lower()
    if "filing" in t or "rapport" in t or "annual report" in t:
        return "filings"
    if "compare" in t or "vs" in t:
        return "compare"
    if any(
        k in t
        for k in [
            "revenue",
            "ebit",
            "ebitda",
            "net income",
            "equity",
            "employees",
            "turnover",
            "omsætning",
        ]
    ):
        return "financials"
    return "profile"


async def _resolve_company(text: str, ctx_company_cvr: str | None):
    cvrs = CVR_RE.findall(text)
    if cvrs:
        return cvrs[0], None
    # fall back to search by name fragments
    tokens = [w for w in re.split(r"[^A-Za-z0-9\-]+", text) if w]
    query = " ".join(tokens[:5]) if tokens else ""
    if query:
        matches = await tool_search_company(query=query, limit=5)
        if len(matches) == 1:
            return matches[0]["cvr"], None
        if len(matches) > 1:
            return None, matches
    return (ctx_company_cvr or None), None


async def handle_chat(req: ChatRequest) -> ChatResponse:
    thread_id = get_or_create_thread(req.thread_id)
    user_msg = next((m.content for m in reversed(req.messages) if m.role == "user"), "").strip()
    ctx = get_ctx(thread_id)
    if req.cvr:
        ctx["cvr"] = req.cvr
    if req.years:
        ctx["years"] = req.years

    # 1) resolve company (allow using context)
    cvr, choices = await _resolve_company(user_msg, ctx.get("cvr"))
    if choices is not None:
        return ChatResponse(
            thread_id=thread_id,
            blocks=[
                ChoiceBlock(
                    prompt="I found multiple companies. Pick one:",
                    choices=[
                        ChoiceItem(
                            id=str(c["cvr"]),
                            label=f"{c['name']} ({c['cvr']})",
                            description=c.get("city"),
                        )
                        for c in choices
                    ],
                )
            ],
        )
    if not cvr:
        return ChatResponse(
            thread_id=thread_id,
            blocks=[TextBlock(text="Please provide a company name or CVR (8 digits).")],
        )

    set_ctx(thread_id, cvr=cvr)

    # 2) choose intent & years
    intent = _intent(user_msg)
    years = _parse_years(user_msg) or ctx.get("years")

    blocks: List[Union[TextBlock, CardBlock, TableBlock, ChoiceBlock]] = []

    if intent == "profile":
        comp = await tool_get_company(cvr)
        blocks.append(
            CardBlock(
                title=f"{comp.get('name', '')} · {cvr}",
                kv={
                    "Status": comp.get("status", ""),
                    "City": comp.get("city", ""),
                    "Industry": comp.get("nace", ""),
                    "Last accounts year": str(comp.get("last_accounts_year", "")),
                },
            )
        )
        blocks.append(
            TextBlock(text="Ask for revenue, EBITDA, equity, employees, filings, or a comparison.")
        )

    elif intent == "financials":
        fin = await tool_get_financials(cvr=cvr, years=years, metrics=None)
        cols = ["Year", "Revenue", "EBIT", "EBITDA", "Net income", "Equity", "Employees"]
        rows = []
        for y in fin.get("years", []):
            rows.append(
                [
                    str(y),
                    fin.get("revenue", {}).get(str(y), "—"),
                    fin.get("ebit", {}).get(str(y), "—"),
                    fin.get("ebitda", {}).get(str(y), "—"),
                    fin.get("net_income", {}).get(str(y), "—"),
                    fin.get("equity", {}).get(str(y), "—"),
                    fin.get("employees", {}).get(str(y), "—"),
                ]
            )
        tbl = TableBlock(
            caption=f"Financials for {cvr}",
            columns=cols,
            rows=rows,
            footnote="All figures as reported in CVR. Year = reporting year.",
        )
        blocks.append(tbl)
        set_last_table(thread_id, {"columns": cols, "rows": rows, "caption": tbl.caption})

    elif intent == "filings":
        filings = await tool_list_filings(cvr, limit=5)
        cols = ["Date", "Type", "Id/Link"]
        rows = [[f.get("date", ""), f.get("type", ""), f.get("id", "")] for f in filings]
        tbl = TableBlock(caption=f"Latest filings for {cvr}", columns=cols, rows=rows)
        blocks.append(tbl)
        set_last_table(thread_id, {"columns": cols, "rows": rows, "caption": tbl.caption})

    elif intent == "compare":
        # MVP: compare the same company across years
        yrs = years or []
        if len(yrs) < 2:
            blocks.append(
                TextBlock(
                    text="Please specify at least two years to compare (e.g., 2021 and 2023)."
                )
            )
        else:
            fin = await tool_get_financials(cvr=cvr, years=yrs, metrics=["revenue", "ebitda"])
            cols = ["Metric"] + [str(y) for y in yrs]
            rows = []
            for metric in ["revenue", "ebitda"]:
                rows.append([metric.upper()] + [fin.get(metric, {}).get(str(y), "—") for y in yrs])
            tbl = TableBlock(caption=f"Comparison for {cvr}", columns=cols, rows=rows)
            blocks.append(tbl)
            set_last_table(thread_id, {"columns": cols, "rows": rows, "caption": tbl.caption})

    return ChatResponse(thread_id=thread_id, blocks=blocks)
