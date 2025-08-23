from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta, UTC
from typing import Optional, List
from cvrgpt_core.models import EventFilter
from cvrgpt_core.providers.erst_events import ErstEventsProvider

router = APIRouter(prefix="/v1/events", tags=["events"])
_provider = ErstEventsProvider()

def _parse_date(s: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(s) if s else None

@router.get("")
def list_events(
    event_type: Optional[str] = Query(None),
    nace: Optional[List[str]] = Query(None, description="NACE prefixes"),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    last_days: Optional[int] = Query(None, ge=1, le=365),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    df = _parse_date(from_date)
    dt = _parse_date(to_date)
    if last_days and (df or dt):
        raise HTTPException(status_code=400, detail="Use either last_days or explicit dates, not both.")
    if last_days:
        dt = datetime.now(UTC)
        df = dt - timedelta(days=last_days)

    filters = EventFilter(
        event_type=event_type,
        nace_prefixes=nace,
        date_from=df,
        date_to=dt,
        limit=limit,
        offset=offset
    )
    items = _provider.list_events(filters)
    return {
        "items": [dict(
            cvr=i.cvr, name=i.name, event_type=i.event_type,
            event_subtype=i.event_subtype, nace=i.nace,
            event_date=i.event_date.isoformat(), source_id=i.source_id, source_url=i.source_url
        ) for i in items],
        "count": len(items),
        "limit": limit,
        "offset": offset
    }
