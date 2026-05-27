from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.discipline import Discipline


class TemplateFieldSchema(BaseModel):
    label: str
    type: str
    unit: Optional[str] = None


class ExperimentTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    discipline: Discipline
    fields: List[TemplateFieldSchema]
    created_at: datetime
