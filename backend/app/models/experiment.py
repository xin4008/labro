from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.template import ExperimentTemplate


class ExperimentStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    URL = "url"


class FieldType(str, enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    IMAGE = "image"


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    status: Mapped[ExperimentStatus] = mapped_column(
        Enum(ExperimentStatus), default=ExperimentStatus.DRAFT, nullable=False
    )
    template_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("experiment_templates.id"), nullable=True
    )
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reagents_instruments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    global_safety_notes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    parsed_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    current_step_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    template: Mapped[ExperimentTemplate | None] = relationship(back_populates="experiments")
    steps: Mapped[list[ExperimentStep]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan", order_by="ExperimentStep.order_index"
    )
    documents: Mapped[list[UploadedDocument]] = relationship(
        back_populates="experiment", cascade="all, delete-orphan"
    )


class ExperimentStep(Base):
    __tablename__ = "experiment_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, default="", nullable=False)
    expected_phenomenon: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phenomenon_source: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    safety_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    field_schema: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    experiment: Mapped[Experiment] = relationship(back_populates="steps")
    records: Mapped[list[StepRecord]] = relationship(
        back_populates="step", cascade="all, delete-orphan"
    )


class StepRecord(Base):
    __tablename__ = "step_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    step_id: Mapped[int] = mapped_column(
        ForeignKey("experiment_steps.id", ondelete="CASCADE"), nullable=False, index=True
    )
    field_label: Mapped[str] = mapped_column(String(128), nullable=False)
    field_type: Mapped[FieldType] = mapped_column(Enum(FieldType), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    text_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    number_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    image_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    step: Mapped[ExperimentStep] = relationship(back_populates="records")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[str] = mapped_column(
        ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    doc_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    is_handout: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    stored_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    parsed_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    experiment: Mapped[Experiment] = relationship(back_populates="documents")
