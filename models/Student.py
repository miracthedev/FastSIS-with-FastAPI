from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID

from .StudentLectureLink import StudentLectureLink

#TODO: use RELATIONSHIP() instead of Field()

if TYPE_CHECKING:
    from models import Student, Teacher, Class, Department, Lecture
    
class Student(SQLModel, table=True):
    model_config = {"extra": "forbid"}
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    fullname: str = "NaN"
    department: str = "NaN"
    grade: int = -1
    gpa: float = Field(default=0.0, decimal_places=2, max_digits=3, le=4, ge=0)
    year_of_entry: int | None = None
    class_id: int | None = Field(default=None, foreign_key="class.id")
    dept_id: int | None = Field(default=None, foreign_key="department.id")
    department: Optional["Department"] = Relationship(back_populates="students")
    student_class: Optional["Class"] = Relationship(back_populates="students")
    lectures: list["Lecture"] = Relationship(
        back_populates="students", 
        link_model=StudentLectureLink
    )

class StudentUpdate(SQLModel):
    model_config = {"extra": "forbid"}
    fullname: str | None = None
    department: str | None = None
    grade: int | None = None
    gpa: float | None = None
    year_of_entry: int | None = None
    class_id: int | None = Field(default=None, foreign_key="class.id")
    dept_id: int | None = Field(default=None, foreign_key="department.id")
