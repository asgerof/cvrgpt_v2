from typing import Any, Dict
from datetime import datetime, timedelta
from cvrgpt_core.providers.erst_events import ErstEventsProvider
from cvrgpt_core.models import EventFilter

_events = ErstEventsProvider()

def tool_events_search(args: Dict[str, Any]) -> Dict[str, Any]:
    filters = EventFilter(
        event_type=args.get("event_type"),
        nace_prefixes=args.get("nace_prefixes"),
        date_from=datetime.fromisoformat(args["date_from"]) if args.get("date_from") else None,
        date_to=datetime.fromisoformat(args["date_to"]) if args.get("date_to") else None,
        limit=int(args.get("limit", 50)),
        offset=int(args.get("offset", 0)),
    )
    items = _events.list_events(filters)
    return {"type": "table", "columns": ["CVR","Name","Type","Subtype","NACE","Date"],
            "rows": [[i.cvr, i.name, i.event_type, i.event_subtype, i.nace, i.event_date.date().isoformat()] for i in items]}

TOOLS = {
    "events_search": {
        "schema": {
            "type": "object",
            "properties": {
                "event_type": {"type":"string"},
                "nace_prefixes": {"type":"array","items":{"type":"string"}},
                "date_from": {"type":"string"},
                "date_to": {"type":"string"},
                "limit": {"type":"integer"},
                "offset": {"type":"integer"}
            },
            "required": ["event_type"]
        },
        "fn": tool_events_search
    }
}
