from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.discipline import Discipline
from app.models.template import ExperimentTemplate
from app.schemas.template import ExperimentTemplateRead

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[ExperimentTemplateRead])
def list_templates(
    discipline: Optional[Discipline] = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ExperimentTemplate]:
    stmt = select(ExperimentTemplate).order_by(ExperimentTemplate.id)
    if discipline is not None:
        stmt = stmt.where(ExperimentTemplate.discipline == discipline)
    return list(db.scalars(stmt).all())
