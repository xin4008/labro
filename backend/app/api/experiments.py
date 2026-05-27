from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.experiment import Experiment, ExperimentStatus, ExperimentStep
from app.models.template import ExperimentTemplate
from app.schemas.experiment import (
    ExperimentCreate,
    ExperimentDetail,
    ExperimentListItem,
    ExperimentUpdate,
)
from app.schemas.literature import DocumentRead
from app.services.export_docx import export_experiment_to_docx

router = APIRouter(prefix="/experiments", tags=["experiments"])


def _to_document_reads(exp: Experiment) -> list[DocumentRead]:
    return [
        DocumentRead(
            id=d.id,
            filename=d.filename,
            doc_type=d.doc_type.value,
            is_handout=d.is_handout,
            source_url=d.source_url,
            created_at=d.created_at,
            has_text=bool(d.parsed_text),
        )
        for d in exp.documents
    ]


def _experiment_or_404(db: Session, experiment_id: str) -> ExperimentDetail:
    exp = db.scalar(
        select(Experiment)
        .where(Experiment.id == experiment_id)
        .options(
            selectinload(Experiment.steps).selectinload(ExperimentStep.records),
            selectinload(Experiment.template),
            selectinload(Experiment.documents),
        )
    )
    if not exp:
        raise HTTPException(status_code=404, detail="实验不存在")
    detail = ExperimentDetail.model_validate(exp)
    detail.documents = _to_document_reads(exp)
    return detail


@router.get("", response_model=list[ExperimentListItem])
def list_experiments(db: Session = Depends(get_db)) -> list[ExperimentListItem]:
    experiments = db.scalars(
        select(Experiment)
        .options(selectinload(Experiment.steps))
        .order_by(Experiment.updated_at.desc())
    ).all()
    result: list[ExperimentListItem] = []
    for exp in experiments:
        steps = exp.steps
        result.append(
            ExperimentListItem(
                id=exp.id,
                title=exp.title,
                status=exp.status,
                template_id=exp.template_id,
                current_step_index=exp.current_step_index,
                created_at=exp.created_at,
                updated_at=exp.updated_at,
                step_count=len(steps),
                completed_step_count=sum(1 for s in steps if s.is_completed),
            )
        )
    return result


@router.post("", response_model=ExperimentDetail, status_code=201)
def create_experiment(
    payload: ExperimentCreate, db: Session = Depends(get_db)
) -> ExperimentDetail:
    if payload.template_id is not None:
        template = db.get(ExperimentTemplate, payload.template_id)
        if not template:
            raise HTTPException(status_code=400, detail="数据模板不存在")

    exp = Experiment(
        title=payload.title.strip(),
        template_id=payload.template_id,
        status=ExperimentStatus.DRAFT,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _experiment_or_404(db, exp.id)


@router.get("/{experiment_id}", response_model=ExperimentDetail)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)) -> ExperimentDetail:
    return _experiment_or_404(db, experiment_id)


@router.put("/{experiment_id}", response_model=ExperimentDetail)
def update_experiment(
    experiment_id: str, payload: ExperimentUpdate, db: Session = Depends(get_db)
) -> ExperimentDetail:
    exp_row = db.scalar(
        select(Experiment)
        .where(Experiment.id == experiment_id)
        .options(
            selectinload(Experiment.steps).selectinload(ExperimentStep.records),
            selectinload(Experiment.template),
            selectinload(Experiment.documents),
        )
    )
    if not exp_row:
        raise HTTPException(status_code=404, detail="实验不存在")
    exp = exp_row
    data = payload.model_dump(exclude_unset=True)
    if "template_id" in data and data["template_id"] is not None:
        template = db.get(ExperimentTemplate, data["template_id"])
        if not template:
            raise HTTPException(status_code=400, detail="数据模板不存在")
    for key, value in data.items():
        setattr(exp, key, value)
    db.commit()
    return _experiment_or_404(db, experiment_id)


@router.get("/{experiment_id}/export-word")
def export_word(experiment_id: str, db: Session = Depends(get_db)):
    exp = db.scalar(
        select(Experiment)
        .where(Experiment.id == experiment_id)
        .options(
            selectinload(Experiment.steps).selectinload(ExperimentStep.records),
        )
    )
    if not exp:
        raise HTTPException(status_code=404, detail="实验不存在")
    if not exp.steps:
        raise HTTPException(status_code=400, detail="尚无实验步骤，无法导出报告")

    try:
        filepath = export_experiment_to_docx(exp)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"导出失败：{exc}") from exc

    filename = filepath.name
    encoded = quote(filename)
    return FileResponse(
        path=str(filepath),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded}"},
    )


@router.delete("/{experiment_id}")
def delete_experiment(experiment_id: str, db: Session = Depends(get_db)) -> dict[str, bool]:
    exp = db.get(Experiment, experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="实验不存在")
    db.delete(exp)
    db.commit()
    return {"ok": True}
