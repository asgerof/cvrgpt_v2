"""
Pydantic response models for CVRGPT v2.
These mirror the REST/MCP contracts to keep schema stable and self-documenting.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: Optional[str] = None
    path: Optional[str] = None
    url: Optional[str] = None
    type: Optional[Literal["ixbrl", "pdf", "fixtures", "api"]] = None
    tag: Optional[str] = None
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
    year: Optional[int] = None


class ProfitAndLoss(BaseModel):
    revenue: Optional[float] = None
    ebit: Optional[float] = None


class BalanceSheet(BaseModel):
    assets: Optional[float] = None
    equity: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None


class AccountPeriod(BaseModel):
    period: Optional[Period] = None
    pl: Optional[ProfitAndLoss] = None
    bs: Optional[BalanceSheet] = None
    citations: List[Citation] = Field(default_factory=list)


class AccountsResponse(BaseModel):
    accounts: dict  # { "current": AccountPeriod, "previous": AccountPeriod }
    citations: List[Citation] = Field(default_factory=list)


# /v1/compare/{cvr}
class Ratios(BaseModel):
    margin: Optional[float] = None
    solvency: Optional[float] = None
    liquidity: Optional[float] = None


class Comparison(BaseModel):
    current: Ratios
    previous: Ratios
    delta: Ratios


class CompareResponse(BaseModel):
    comparison: Optional[Comparison] = None
    narrative: str
    citations: List[Citation] = Field(default_factory=list)
