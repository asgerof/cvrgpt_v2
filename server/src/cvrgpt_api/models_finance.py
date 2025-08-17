"""
Financial models using Decimal for precise monetary calculations.
"""

from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ConfiguredBaseModel(BaseModel):
    """Base model with Decimal serialization configured."""
    
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: str(v) if v is not None else None}
    )


class Period(BaseModel):
    start_date: Optional[str] = None  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD
    year: Optional[int] = None


class Citation(BaseModel):
    source_id: Optional[str] = None  # internal reference
    url: str
    label: str
    accessed_at: Optional[str] = None  # ISO timestamp
    type: Optional[str] = None
    page: Optional[int] = None


class AccountLine(ConfiguredBaseModel):
    """Represents a single financial metric with precise decimal value."""
    metric: str
    value: Optional[Decimal] = None  # money or ratio
    currency: Optional[str] = None
    period: str  # e.g. '2024'


class AccountsSnapshot(ConfiguredBaseModel):
    """Financial snapshot with Decimal precision for all monetary values."""
    period: Optional[Period] = None
    revenue: Optional[Decimal] = None
    ebit: Optional[Decimal] = None  # operating profit
    net_income: Optional[Decimal] = None
    assets: Optional[Decimal] = None
    equity: Optional[Decimal] = None
    cash: Optional[Decimal] = None
    current_assets: Optional[Decimal] = None
    current_liabilities: Optional[Decimal] = None
    source_anchors: List[Citation] = Field(default_factory=list)  # per-field citations


class AccountsResponse(ConfiguredBaseModel):
    current: Optional[AccountsSnapshot] = None
    previous: Optional[AccountsSnapshot] = None
    citations: List[Citation] = Field(default_factory=list)


class AccountsDelta(ConfiguredBaseModel):
    """Financial comparison with Decimal precision."""
    field: str
    current_value: Optional[Decimal] = None
    previous_value: Optional[Decimal] = None
    absolute_change: Optional[Decimal] = None
    percentage_change: Optional[Decimal] = None  # Also using Decimal for percentages


class CompareResponse(ConfiguredBaseModel):
    current_period: Optional[str] = None  # "2024"
    previous_period: Optional[str] = None  # "2023"
    key_changes: List[AccountsDelta] = Field(default_factory=list)
    narrative: str
    sources: List[Citation] = Field(default_factory=list)
