import os
import json
import httpx
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, UTC
from ..tools.registry import TOOLS
from cvrgpt_core.accounts.extract import get_annual_result
from ..security import require_api_key
from ..logging import setup_logging


def get_rate_limiter(times: int, seconds: int):
    """Local rate limiter helper to avoid circular import with api.py.
    Returns a dependency callable if fastapi-limiter is available and initialized; otherwise no-op.
    """
    try:
        from fastapi_limiter.depends import RateLimiter  # type: ignore
        from fastapi_limiter import FastAPILimiter  # type: ignore
    except Exception:
        return lambda: None

    def rate_limit_check():
        try:
            if not hasattr(FastAPILimiter, "redis") or FastAPILimiter.redis is None:
                return None
            return RateLimiter(times=times, seconds=seconds)()
        except Exception:
            return None

    return rate_limit_check


router = APIRouter(prefix="/v1/chat", tags=["chat"])
log = setup_logging()


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    thread_id: str
    messages: List[ChatTurn]


async def _llm_route(user_msg: str) -> Optional[Dict[str, Any]]:
    """
    Try to resolve the user message using an LLM that returns a structured action.
    Returns a dict with keys {"blocks": [...]} on success, or None to fall back.
    Expected actions:
      - {"action": "events_search", "args": {"event_type": "bankruptcy", "nace_prefixes": ["62"], "last_n_months": 3 }}
      - {"action": "annual_result", "args": {"company": "Name", "year": 2022 }}
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("CHAT_NLU_MODEL", "gpt-4o-mini")
    if not api_key:
        return None

    system = (
        "You map user queries about Danish companies into JSON actions. "
        "Only return JSON. Supported actions: \n"
        "- events_search: args: {event_type: string (e.g., bankruptcy), nace_prefixes: string[], last_n_months: int}\n"
        "- annual_result: args: {company: string, year: int}\n"
        'If no suitable action, return {"action": "none"}.'
    )
    user = f"Query: {user_msg}\nReturn JSON only."

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }

    try:
        t0 = time.time()
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=body,
            )
        dt = (time.time() - t0) * 1000
        if r.status_code != 200:
            log.warning(f"v1/chat LLM failed status={r.status_code} time_ms={dt:.0f}")
            return None
        data = r.json()
        content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "{}"
        obj = json.loads(content)
        action = (obj.get("action") or "none").lower()
        args = obj.get("args") or {}

        if action == "events_search":
            months = int(args.get("last_n_months") or 3)
            date_to = datetime.now(UTC)
            date_from = date_to - timedelta(days=30 * months)
            nace = args.get("nace_prefixes") or ["62"]
            result = TOOLS["events_search"]["fn"](
                {
                    "event_type": args.get("event_type") or "bankruptcy",
                    "nace_prefixes": nace,
                    "date_from": date_from.isoformat(),
                    "date_to": date_to.isoformat(),
                    "limit": int(args.get("limit") or 50),
                }
            )
            return {
                "blocks": [
                    {
                        "type": "chips",
                        "items": [
                            {"label": f"type: {args.get('event_type') or 'bankruptcy'}"},
                            {"label": f"nace: {','.join(nace)}"},
                            {"label": f"window: last {months} months"},
                        ],
                    },
                    result,
                ]
            }
        if action == "annual_result":
            company = str(args.get("company") or "").strip().strip('"')
            year = int(args.get("year") or 0)
            if not company or not year:
                return None
            hit = get_annual_result(company, year)
            if not hit:
                return {
                    "blocks": [
                        {
                            "type": "text",
                            "text": f"No annual result found for {company} in {year} (yet).",
                        }
                    ]
                }
            return {
                "blocks": [
                    {"type": "text", "text": f"Annual result ({year}) for {company}:"},
                    {
                        "type": "table",
                        "columns": ["Metric", "Value", "Currency"],
                        "rows": [[hit["label"], f"{hit['value']:,}", hit["currency"]]],
                    },
                    {
                        "type": "text",
                        "subtle": True,
                        "text": f"Source: {hit['source_id']} ({hit['source_url']})",
                    },
                ]
            }
        return None
    except Exception as e:
        log.warning(f"v1/chat LLM exception: {e}")
        return None


@router.post("", dependencies=[Depends(require_api_key), Depends(get_rate_limiter(30, 60))])
async def chat(req: ChatRequest):
    user_msg = req.messages[-1].content.strip() if req.messages else ""
    t0 = time.time()
    llm = await _llm_route(user_msg)
    if not llm or not llm.get("blocks"):
        dt = (time.time() - t0) * 1000
        log.warning(f"v1/chat LLM unavailable time_ms={dt:.0f}")
        raise HTTPException(
            status_code=503,
            detail="LLM NLU unavailable. Ensure OPENAI_API_KEY is configured and the model is reachable.",
        )

    dt = (time.time() - t0) * 1000
    log.info(f"v1/chat handled time_ms={dt:.0f}")
    return {
        "thread_id": req.thread_id,
        "blocks": llm["blocks"],
    }
