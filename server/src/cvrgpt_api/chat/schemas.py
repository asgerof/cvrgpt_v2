from typing import List, Literal, Optional, Union, Dict
from pydantic import BaseModel, Field

Role = Literal["user", "assistant", "tool"]


class ChatTurn(BaseModel):
    role: Role
    content: str


class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    text: str


class CardBlock(BaseModel):
    type: Literal["card"] = "card"
    title: str
    kv: Dict[str, str]  # small key/value snapshot (e.g., status, city, last accounts year)


class TableBlock(BaseModel):
    type: Literal["table"] = "table"
    caption: Optional[str] = None
    columns: List[str]
    rows: List[List[str]]
    footnote: Optional[str] = None


class ChoiceItem(BaseModel):
    id: str
    label: str
    description: Optional[str] = None


class ChoiceBlock(BaseModel):
    type: Literal["choice"] = "choice"
    prompt: str
    choices: List[ChoiceItem]


ChatBlock = Union[TextBlock, CardBlock, TableBlock, ChoiceBlock]


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    messages: List[ChatTurn]
    # optional hints from the UI
    cvr: Optional[str] = None
    years: Optional[List[int]] = None


class ChatResponse(BaseModel):
    thread_id: str
    blocks: List[ChatBlock] = Field(default_factory=list)
