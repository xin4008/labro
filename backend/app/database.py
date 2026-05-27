from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings, resolve_path


class Base(DeclarativeBase):
    pass


def _sqlite_database_url(url: str) -> str:
    if url.startswith("sqlite:///./"):
        rel = url.removeprefix("sqlite:///./")
        abs_path = resolve_path(rel)
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{abs_path.as_posix()}"
    return url


settings = get_settings()
engine = create_engine(
    _sqlite_database_url(settings.database.url),
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import experiment, template  # noqa: F401

    uploads = resolve_path(settings.storage.uploads_dir)
    exports = resolve_path(settings.storage.exports_dir)
    uploads.mkdir(parents=True, exist_ok=True)
    exports.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
