from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.experiments import _experiment_or_404
from app.database import get_db
from app.models.experiment import Experiment, ExperimentStep
from app.schemas.experiment import ExperimentDetail, StepRecordRead
from app.schemas.records import RecordsBatchUpsert, SetCurrentStepBody
from app.services import records as records_service

router = APIRouter(prefix="/experiments", tags=["steps"])


def _get_step(db: Session, experiment_id: str, step_id: int) -> tuple[Experiment, ExperimentStep]:
    exp = db.scalar(
        select(Experiment)
        .where(Experiment.id == experiment_id)
        .options(
            selectinload(Experiment.steps).selectinload(ExperimentStep.records),
            selectinload(Experiment.documents),
            selectinload(Experiment.template),
        )
    )
    if not exp:
        raise HTTPException(status_code=404, detail="实验不存在")
    step = next((s for s in exp.steps if s.id == step_id), None)
    if not step:
        raise HTTPException(status_code=404, detail="步骤不存在")
    return exp, step


@router.put("/{experiment_id}/steps/{step_id}/records", response_model=list[StepRecordRead])
def save_records(
    experiment_id: str,
    step_id: int,
    payload: RecordsBatchUpsert,
    db: Session = Depends(get_db),
) -> list[StepRecordRead]:
    exp, step = _get_step(db, experiment_id, step_id)
    records_service.upsert_records(db, step, payload.records)
    db.refresh(step)
    return [StepRecordRead.model_validate(r) for r in step.records]


@router.post("/{experiment_id}/steps/{step_id}/records/image", response_model=StepRecordRead)
async def upload_record_image(
    experiment_id: str,
    step_id: int,
    field_label: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> StepRecordRead:
    exp, step = _get_step(db, experiment_id, step_id)
    try:
        record = records_service.save_step_image(db, exp, step, field_label, file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StepRecordRead.model_validate(record)


@router.post("/{experiment_id}/steps/{step_id}/complete", response_model=ExperimentDetail)
def complete_step(
    experiment_id: str, step_id: int, db: Session = Depends(get_db)
) -> ExperimentDetail:
    exp, step = _get_step(db, experiment_id, step_id)
    records_service.complete_step(db, exp, step)
    return _experiment_or_404(db, experiment_id)


@router.post("/{experiment_id}/steps/{step_id}/reopen", response_model=ExperimentDetail)
def reopen_step(
    experiment_id: str, step_id: int, db: Session = Depends(get_db)
) -> ExperimentDetail:
    exp, step = _get_step(db, experiment_id, step_id)
    records_service.reopen_step(db, exp, step)
    return _experiment_or_404(db, experiment_id)


@router.put("/{experiment_id}/current-step", response_model=ExperimentDetail)
def set_current_step(
    experiment_id: str,
    payload: SetCurrentStepBody,
    db: Session = Depends(get_db),
) -> ExperimentDetail:
    exp = db.scalar(
        select(Experiment)
        .where(Experiment.id == experiment_id)
        .options(selectinload(Experiment.steps))
    )
    if not exp:
        raise HTTPException(status_code=404, detail="实验不存在")
    try:
        records_service.set_current_step_index(db, exp, payload.step_index)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _experiment_or_404(db, experiment_id)
