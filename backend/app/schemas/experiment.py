from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.experiment import ExperimentStatus, FieldType
from app.schemas.literature import DocumentRead


class ExperimentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    template_id: Optional[int] = None


class ExperimentUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=256)
    status: Optional[ExperimentStatus] = None
    template_id: Optional[int] = None
    purpose: Optional[str] = None
    reagents_instruments: Optional[list] = None
    global_safety_notes: Optional[list] = None
    current_step_index: Optional[int] = None


class StepRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    field_label: str
    field_type: FieldType
    unit: Optional[str]
    text_value: Optional[str]
    number_value: Optional[float]
    image_path: Optional[str]
    updated_at: datetime


class ExperimentStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_index: int
    title: str
    instructions: str
    expected_phenomenon: Optional[str]
    phenomenon_source: Optional[str]
    safety_notes: Optional[str]
    field_schema: Optional[list]
    is_completed: bool
    completed_at: Optional[datetime]
    records: List[StepRecordRead] = []


class ExperimentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: ExperimentStatus
    template_id: Optional[int]
    current_step_index: int
    created_at: datetime
    updated_at: datetime
    step_count: int = 0
    completed_step_count: int = 0


class ExperimentDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: ExperimentStatus
    template_id: Optional[int]
    purpose: Optional[str]
    reagents_instruments: Optional[list]
    global_safety_notes: Optional[list]
    parsed_metadata: Optional[dict]
    current_step_index: int
    created_at: datetime
    updated_at: datetime
    steps: List[ExperimentStepRead] = []
    documents: List[DocumentRead] = []
