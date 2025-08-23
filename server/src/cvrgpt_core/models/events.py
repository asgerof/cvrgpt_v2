from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Event:
    cvr: str
    name: str
    event_type: str  # e.g., "bankruptcy"
    event_subtype: Optional[str]  # e.g., "declaration", "petition"
    nace: Optional[str]
    event_date: datetime
    source_id: Optional[str]  # provider-specific id
    source_url: Optional[str]


@dataclass
class EventFilter:
    event_type: Optional[str] = None
    nace_prefixes: Optional[List[str]] = None  # e.g., ["62", "62.0"]
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 50
    offset: int = 0
