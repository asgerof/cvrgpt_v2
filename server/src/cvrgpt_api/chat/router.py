from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from io import StringIO
from .schemas import ChatRequest, ChatResponse
from .orchestrator import handle_chat
from .state import get_last_table
from ..security import require_api_key

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, _: str = Depends(require_api_key)):
    """Handle chat requests with structured response blocks"""
    return await handle_chat(req)


@router.get("/export")
async def export_csv(thread_id: str, _: str = Depends(require_api_key)):
    """Export the last table from a chat thread as CSV"""
    tbl = get_last_table(thread_id)
    if not tbl:
        raise HTTPException(status_code=400, detail="No table to export in this thread.")

    out = StringIO()
    cols = tbl["columns"]
    rows = tbl["rows"]
    out.write(",".join(cols) + "\n")
    for row in rows:
        out.write(",".join([str(c).replace(",", " ") for c in row]) + "\n")
    out.seek(0)

    return StreamingResponse(
        iter([out.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=export.csv"},
    )
