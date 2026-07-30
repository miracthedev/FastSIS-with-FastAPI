from logging import INFO, log
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from datetime import datetime

log(msg="Delve deep on this",level=INFO)
# 1. Use TYPE_CHECKING to prevent circular import crashes
if TYPE_CHECKING:
    # 2. Add the dot (.) before Teacher to tell Python it is in the same folder
    from .Teacher import Teacher
    from .Student import Student
    from .Lecture import Lecture

#TODO: use RELATIONSHIP() instead of Field()

class Department(SQLModel, table=True):
    # department_id: UUID | None = None
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field( default_factory=datetime.now)
    department_name: str | None = None
# Relationships mapping back to the child tables
    teachers: list["Teacher"] = Relationship(back_populates="department")   
    students: list["Student"] = Relationship(back_populates="department")
    lectures: list["Lecture"] = Relationship(back_populates="department")
