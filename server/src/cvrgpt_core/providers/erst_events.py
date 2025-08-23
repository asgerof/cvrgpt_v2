import json
import os
import requests
from datetime import datetime
from pathlib import Path
from typing import List
from ..models import Event, EventFilter
from .base import EventsProvider

USE_REAL = os.getenv("ERST_EVENTS_REAL", "0") == "1"
ERST_BASE = os.getenv("ERST_API_BASE", "https://erst.example")
ERST_KEY = os.getenv("ERST_API_KEY", "")

_FIXTURE = Path(__file__).with_suffix("").parent / "fixtures" / "erst_events.json"


class ErstEventsProvider(EventsProvider):
    def list_events(self, filters: EventFilter) -> List[Event]:
        if not USE_REAL:
            return self._list_fixture(filters)
        # PSEUDO — replace with real ERST endpoint/params when available:
        params = {
            "type": filters.event_type,
            "nace": ",".join(filters.nace_prefixes or []),
            "from": filters.date_from.isoformat() if filters.date_from else None,
            "to": filters.date_to.isoformat() if filters.date_to else None,
            "limit": filters.limit,
            "offset": filters.offset,
        }
        headers = {"Authorization": f"Bearer {ERST_KEY}"} if ERST_KEY else {}
        r = requests.get(
            f"{ERST_BASE}/events",
            params={k: v for k, v in params.items() if v is not None},
            headers=headers,
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        # Map payload → Event list (adapt fields to actual ERST schema)
        # TODO: implement mapping when real ERST schema is available
        return []

    def _list_fixture(self, filters: EventFilter) -> List[Event]:
        """Fallback to fixture data"""
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
