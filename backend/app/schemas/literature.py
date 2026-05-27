from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    doc_type: str
    is_handout: bool
    source_url: Optional[str]
    created_at: datetime
    has_text: bool = False


class UrlDocumentCreate(BaseModel):
    url: str = Field(min_length=8, max_length=1024)
    is_handout: bool = False


class ParseLiteratureResponse(BaseModel):
    experiment_id: str
    steps_generated: int
    message: str
