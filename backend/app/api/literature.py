import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session, selectinload

from app.api.experiments import _experiment_or_404
from app.database import get_db
from app.models.experiment import Experiment
from app.schemas.experiment import ExperimentDetail
from app.schemas.literature import DocumentRead, ParseLiteratureResponse, UrlDocumentCreate
from app.services import literature as literature_service

router = APIRouter(prefix="/experiments", tags=["literature"])


def _experiment_with_docs(db: Session, experiment_id: str) -> Experiment:
    from sqlalchemy import select

    exp = db.scalar(
        select(Experiment)
        .where(Experiment.id == experiment_id)
        .options(
            selectinload(Experiment.documents),
            selectinload(Experiment.steps),
            selectinload(Experiment.template),
        )
    )
    if not exp:
        raise HTTPException(status_code=404, detail="实验不存在")
    return exp


@router.get("/{experiment_id}/documents", response_model=list[DocumentRead])
def list_documents(experiment_id: str, db: Session = Depends(get_db)) -> list[DocumentRead]:
    exp = _experiment_with_docs(db, experiment_id)
    return [literature_service.build_document_read(d, experiment_id) for d in exp.documents]


@router.post("/{experiment_id}/documents/upload", response_model=list[DocumentRead])
async def upload_document(
    experiment_id: str,
    file: UploadFile = File(...),
    is_handout: bool = Form(False),
    db: Session = Depends(get_db),
) -> list[DocumentRead]:
    exp = _experiment_with_docs(db, experiment_id)
    try:
        literature_service.save_uploaded_file(db, exp, file, is_handout)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    exp = _experiment_with_docs(db, experiment_id)
    return [literature_service.build_document_read(d, experiment_id) for d in exp.documents]


@router.post("/{experiment_id}/documents/url", response_model=list[DocumentRead])
async def add_url(
    experiment_id: str,
    payload: UrlDocumentCreate,
    db: Session = Depends(get_db),
) -> list[DocumentRead]:
    exp = _experiment_with_docs(db, experiment_id)
    try:
        await literature_service.add_url_document(
            db, exp, payload.url.strip(), payload.is_handout
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=400, detail=f"网址抓取失败：{exc}") from exc
    except Exception as exc:
        detail = str(exc).strip() or "未知错误"
        if not detail.startswith("该") and not detail.startswith("中国"):
            detail = f"网址抓取失败：{detail}"
        raise HTTPException(status_code=400, detail=detail) from exc

    exp = _experiment_with_docs(db, experiment_id)
    return [literature_service.build_document_read(d, experiment_id) for d in exp.documents]


@router.delete("/{experiment_id}/documents/{document_id}")
def remove_document(
    experiment_id: str, document_id: int, db: Session = Depends(get_db)
) -> dict[str, bool]:
    exp = _experiment_with_docs(db, experiment_id)
    try:
        literature_service.delete_document(db, exp, document_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True}


@router.post("/{experiment_id}/parse", response_model=ExperimentDetail)
async def parse_literature(
    experiment_id: str, db: Session = Depends(get_db)
) -> ExperimentDetail:
    exp = _experiment_with_docs(db, experiment_id)
    try:
        await literature_service.parse_and_generate_steps(db, exp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        msg = str(exc).strip() or type(exc).__name__
        raise HTTPException(
            status_code=502,
            detail=f"{msg}。已上传的文献未受影响，请检查后重试。",
        ) from exc

    return _experiment_or_404(db, experiment_id)
