from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings, resolve_path
from app.models.experiment import Experiment, ExperimentStep, FieldType, StepRecord
from app.schemas.records import RecordUpsertItem

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024


def _step_images_dir(experiment_id: str, step_id: int) -> Path:
    settings = get_settings()
    base = resolve_path(settings.storage.uploads_dir) / experiment_id / "steps" / str(step_id)
    base.mkdir(parents=True, exist_ok=True)
    return base


def upsert_records(
    db: Session, step: ExperimentStep, items: list[RecordUpsertItem]
) -> list[StepRecord]:
    existing = {r.field_label: r for r in step.records}
    result: list[StepRecord] = []

    for item in items:
        record = existing.get(item.field_label)
        if record is None:
            record = StepRecord(
                step_id=step.id,
                field_label=item.field_label,
                field_type=item.field_type,
                unit=item.unit,
            )
            db.add(record)
            existing[item.field_label] = record

        record.field_type = item.field_type
        record.unit = item.unit
        if item.field_type == FieldType.TEXT:
            record.text_value = item.text_value
            record.number_value = None
        elif item.field_type == FieldType.NUMBER:
            record.number_value = item.number_value
            record.text_value = None
        result.append(record)

    db.commit()
    for r in result:
        db.refresh(r)
    return result


def save_step_image(
    db: Session,
    experiment: Experiment,
    step: ExperimentStep,
    field_label: str,
    file: UploadFile,
) -> StepRecord:
    filename = file.filename or "image.jpg"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXT:
        raise ValueError(f"不支持的图片格式 {ext}")

    content = file.file.read()
    if len(content) > MAX_IMAGE_BYTES:
        raise ValueError("图片不能超过 8MB")

    dest_dir = _step_images_dir(experiment.id, step.id)
    safe_name = f"{field_label}_{len(list(dest_dir.glob('*')))}{ext}".replace("/", "_")
    dest_path = dest_dir / safe_name
    dest_path.write_bytes(content)

    rel_path = f"/api/files/{experiment.id}/steps/{step.id}/{safe_name}"

    record = next((r for r in step.records if r.field_label == field_label), None)
    if record is None:
        record = StepRecord(
            step_id=step.id,
            field_label=field_label,
            field_type=FieldType.IMAGE,
        )
        db.add(record)
    record.field_type = FieldType.IMAGE
    record.image_path = rel_path
    record.text_value = None
    record.number_value = None
    db.commit()
    db.refresh(record)
    return record


def complete_step(db: Session, experiment: Experiment, step: ExperimentStep) -> None:
    from datetime import datetime, timezone

    step.is_completed = True
    step.completed_at = datetime.now(timezone.utc)
    from app.models.experiment import ExperimentStatus

    if experiment.status == ExperimentStatus.DRAFT:
        experiment.status = ExperimentStatus.IN_PROGRESS

    next_index = step.order_index + 1
    if next_index > experiment.current_step_index:
        experiment.current_step_index = min(next_index, len(experiment.steps) - 1)

    all_done = all(s.is_completed for s in experiment.steps)
    if all_done:
        experiment.status = ExperimentStatus.COMPLETED

    db.commit()


def reopen_step(db: Session, experiment: Experiment, step: ExperimentStep) -> None:
    step.is_completed = False
    step.completed_at = None
    from app.models.experiment import ExperimentStatus

    if experiment.status == ExperimentStatus.COMPLETED:
        experiment.status = ExperimentStatus.IN_PROGRESS
    if step.order_index < experiment.current_step_index:
        experiment.current_step_index = step.order_index
    db.commit()


def set_current_step_index(db: Session, experiment: Experiment, step_index: int) -> None:
    if step_index < 0 or step_index >= len(experiment.steps):
        raise ValueError("步骤序号无效")
    steps = sorted(experiment.steps, key=lambda s: s.order_index)
    # 前进：上一 step 必须已完成；后退：允许回到任意已访问步骤
    if step_index > experiment.current_step_index and step_index > 0:
        if not steps[step_index - 1].is_completed:
            raise ValueError("请先完成上一步骤，再进入下一步")
    experiment.current_step_index = step_index
    db.commit()
