from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, create_engine
from models import Class, Department, Lecture, Student, Teacher

def start_db():
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    engine = create_engine(sqlite_url, echo=True)

    SQLModel.metadata.create_all(engine)

    return engine