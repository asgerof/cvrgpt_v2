from pydantic import BaseModel
from .common import Source


class Company(BaseModel):
    cvr: str
    name: str
    status: str | None = None
    address: str | None = None
    sources: list[Source]


class SearchItem(BaseModel):
    cvr: str
    name: str
    snippet: str | None = None
    sources: list[Source]


class SearchResponse(BaseModel):
    items: list[SearchItem]
    next_cursor: str | None = None
    has_more: bool = False


class Filing(BaseModel):
    id: str
    date: str
    type: str
    sources: list[Source]


class FilingsResponse(BaseModel):
    items: list[Filing]
    next_cursor: str | None = None
    has_more: bool = False


class AccountSummary(BaseModel):
    cvr: str
    fiscal_year: str
    revenue: float | None = None
    ebit: float | None = None
    equity: float | None = None
    currency: str | None = None
    sources: list[Source]


class CompareItem(BaseModel):
    cvr: str
    name: str
    revenue_delta: float | None = None  # relative change in %
    ebit_delta: float | None = None
    sources: list[Source]


class CompareResponse(BaseModel):
    base: AccountSummary
    peers: list[CompareItem]
    sources: list[Source]
