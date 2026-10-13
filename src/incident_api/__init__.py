import uvicorn
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm.session import Session
from sqlmodel import SQLModel, create_engine

sqlite_file_name = "incident_report.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def main() -> None:
    print("Hello from incident-api!")
    uvicorn.run(
        "incident_api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["src"],
        log_level="debug",
    )
