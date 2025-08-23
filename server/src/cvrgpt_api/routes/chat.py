from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import re
from datetime import datetime, timedelta, UTC
from ..tools.registry import TOOLS

router = APIRouter(prefix="/v1/chat", tags=["chat"])

class ChatTurn(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    thread_id: str
    messages: List[ChatTurn]

@router.post("")
def chat(req: ChatRequest):
    user_msg = req.messages[-1].content.strip()

    # 1) Bankruptcy in IT last N months (en/da)
    pat_bank = re.compile(r"(bankrupt|konkurs).*?(IT|IT\-?branchen|it).*?(last\s*(\d+)\s*months|sidste\s*(\d+)\s*m(åneder)?)", re.I)
    m = pat_bank.search(user_msg)
    if m:
        months = int(m.group(4) or m.group(5) or 3)
        date_to = datetime.now(UTC)
        date_from = date_to - timedelta(days=30*months)
        result = TOOLS["events_search"]["fn"]({
            "event_type":"bankruptcy",
            "nace_prefixes":["62"],
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "limit": 50
        })
        return {
            "thread_id": req.thread_id,
            "blocks": [
                {"type":"chips","items":[
                    {"label":"type: bankruptcy"},
                    {"label":"nace: 62*"},
                    {"label":f"window: last {months} months"}
                ]},
                result
            ]
        }

    # 2) Annual result for company X in YEAR?
    pat_res = re.compile(r"(annual result|årets resultat).*?(?:for|for\s*selskab(et)?|company)\s+(.+?)\s+(?:in|i)\s+(\d{4})\??", re.I)
    m = pat_res.search(user_msg)
    if m:
        company = m.group(3).strip().strip('"')
        year = int(m.group(4))
        # placeholder response; real extraction on Day 5/6
        return {
            "thread_id": req.thread_id,
            "blocks":[
                {"type":"text","text":f"Looking up annual result for {company} ({year})…"},
                {"type":"text","emphasis":"warning","text":"Numeric extraction will be added in the next step."}
            ]
        }

    return {
        "thread_id": req.thread_id,
        "blocks":[
            {"type":"text","text":"I didn't recognize the request. Try:\n- \"recent bankruptcies in the IT sector (last 3 months)\"\n- \"What was the annual result of company X in 2022?\""}
        ]
    }
