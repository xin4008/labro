from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.discipline import Discipline


class ExperimentTemplate(Base):
    __tablename__ = "experiment_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    discipline: Mapped[Discipline] = mapped_column(
        Enum(Discipline, values_callable=lambda x: [e.value for e in x]),
        default=Discipline.CHEMISTRY,
        nullable=False,
    )
    fields: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    experiments: Mapped[list["Experiment"]] = relationship(back_populates="template")
