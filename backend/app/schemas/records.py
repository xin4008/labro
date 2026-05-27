from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.experiment import FieldType


class RecordUpsertItem(BaseModel):
    field_label: str = Field(min_length=1, max_length=128)
    field_type: FieldType
    unit: Optional[str] = None
    text_value: Optional[str] = None
    number_value: Optional[float] = None


class RecordsBatchUpsert(BaseModel):
    records: List[RecordUpsertItem]


class SetCurrentStepBody(BaseModel):
    step_index: int = Field(ge=0)
