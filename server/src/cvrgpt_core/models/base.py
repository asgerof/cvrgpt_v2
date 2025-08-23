from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

class Citation(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    retrieved_at: Optional[str] = None  # ISO 8601

class Company(BaseModel):
    cvr: str = Field(min_length=8, max_length=8)
    name: str
    address: Optional[str] = None

class Filing(BaseModel):
    id: str
    year: int
    type: str
    url: Optional[HttpUrl] = None
    citations: List[Citation] = []

class Accounts(BaseModel):
    year: int
    revenue: Optional[float] = None
    ebit: Optional[float] = None
    equity: Optional[float] = None
    citations: List[Citation] = []

class CompareAccountsResponse(BaseModel):
    a: Accounts
    b: Accounts
    deltas: Dict[str, Optional[float]]
    citations: List[Citation]
