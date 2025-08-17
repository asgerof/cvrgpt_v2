"""
Pydantic response models for CVRGPT v2.
These mirror the REST/MCP contracts to keep schema stable and self-documenting.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source_id: Optional[str] = None  # internal reference
    url: str
    label: str
    accessed_at: Optional[str] = None  # ISO timestamp
    type: Optional[Literal["ixbrl", "pdf", "api", "fixtures"]] = None
    page: Optional[int] = None


# /v1/search
class SearchItem(BaseModel):
    cvr: str
    name: str
    status: Optional[str] = None


class SearchResponse(BaseModel):
    items: List[SearchItem]
    citations: List[Citation] = Field(default_factory=list)


# /v1/company/{cvr}
class Industry(BaseModel):
    code: Optional[str] = None
    text: Optional[str] = None


class Address(BaseModel):
    type: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    zip: Optional[str] = None
    country: Optional[str] = None


class Officer(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None


class Company(BaseModel):
    cvr: str
    name: str
    status: Optional[str] = None
    industry: Optional[Industry] = None
    addresses: List[Address] = Field(default_factory=list)
    officers: List[Officer] = Field(default_factory=list)


class CompanyResponse(BaseModel):
    company: Company
    citations: List[Citation] = Field(default_factory=list)


# /v1/filings/{cvr}
class Filing(BaseModel):
    id: str
    type: str
    date: str
    url: str


class FilingsResponse(BaseModel):
    filings: List[Filing]
    citations: List[Citation] = Field(default_factory=list)


# /v1/accounts/latest/{cvr}
class Period(BaseModel):
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD
    year: Optional[int] = None


class AccountsSnapshot(BaseModel):
    period: Optional[Period] = None
    revenue: Optional[float] = None
    ebit: Optional[float] = None  # operating profit
    net_income: Optional[float] = None
    assets: Optional[float] = None
    equity: Optional[float] = None
    cash: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    source_anchors: List[Citation] = Field(default_factory=list)  # per-field citations


class AccountsResponse(BaseModel):
    current: Optional[AccountsSnapshot] = None
    previous: Optional[AccountsSnapshot] = None
    citations: List[Citation] = Field(default_factory=list)


# /v1/compare/{cvr}
class AccountsDelta(BaseModel):
    field: str
    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None


class CompareResponse(BaseModel):
    current_period: Optional[str] = None  # "2024"
    previous_period: Optional[str] = None  # "2023"
    key_changes: List[AccountsDelta] = Field(default_factory=list)
    narrative: str
    sources: List[Citation] = Field(default_factory=list)
