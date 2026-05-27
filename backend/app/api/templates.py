from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.template import ExperimentTemplate
from app.schemas.template import ExperimentTemplateRead

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[ExperimentTemplateRead])
def list_templates(db: Session = Depends(get_db)) -> list[ExperimentTemplate]:
    return list(db.scalars(select(ExperimentTemplate).order_by(ExperimentTemplate.id)).all())
