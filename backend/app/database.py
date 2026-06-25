from collections.abc import Generator

import os

from sqlmodel import Session, SQLModel, create_engine

# On Vercel the only writable location is /tmp. Vercel sets VERCEL=1 automatically.
_DEFAULT = "sqlite:////tmp/greencast.db" if os.environ.get("VERCEL") else "sqlite:///./greencast.db"
DATABASE_URL = os.environ.get("DATABASE_URL", _DEFAULT)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
