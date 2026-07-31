from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, Session, create_engine
from models import Class, Department, Lecture, Student, Teacher

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)
SQLModel.metadata.create_all(engine)

def start_db():
    return engine

def get_session():
    with Session(engine) as session:
        yield session