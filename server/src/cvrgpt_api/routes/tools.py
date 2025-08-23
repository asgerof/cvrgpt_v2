from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from ..tools.registry import TOOLS

router = APIRouter(prefix="/v1/tools", tags=["tools"])

class ToolRequest(BaseModel):
    name: str
    args: Dict[str, Any] = {}

@router.post("/run")
def run_tool(req: ToolRequest):
    tool = TOOLS.get(req.name)
    if not tool:
        raise HTTPException(404, "Unknown tool")
    # naive schema validation
    fn = tool["fn"]
    return {"ok": True, "result": fn(req.args)}
