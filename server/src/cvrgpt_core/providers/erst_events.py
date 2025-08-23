import json
from datetime import datetime
from pathlib import Path
from typing import List
from ..models import Event, EventFilter
from .base import EventsProvider

_FIXTURE = Path(__file__).with_suffix("").parent / "fixtures" / "erst_events.json"


class ErstEventsProvider(EventsProvider):
    def list_events(self, filters: EventFilter) -> List[Event]:
        data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
        out: List[Event] = []
        for raw in data:
            ev_date = datetime.fromisoformat(raw["event_date"])
            if filters.date_from and ev_date < filters.date_from:
                continue
            if filters.date_to and ev_date > filters.date_to:
                continue
            if filters.event_type and raw["event_type"] != filters.event_type:
                continue
            if filters.nace_prefixes:
                ok = any((raw.get("nace") or "").startswith(pref) for pref in filters.nace_prefixes)
                if not ok:
                    continue
            out.append(
                Event(
                    cvr=raw["cvr"],
                    name=raw["name"],
                    event_type=raw["event_type"],
                    event_subtype=raw.get("event_subtype"),
                    nace=raw.get("nace"),
                    event_date=ev_date,
                    source_id=raw.get("source_id"),
                    source_url=raw.get("source_url"),
                )
            )
        return out[filters.offset : filters.offset + filters.limit]
