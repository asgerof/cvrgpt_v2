from pydantic import BaseModel
from app.models.common import Source


class ProviderResult(BaseModel):
    data: dict
    sources: list[Source]
