from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID



class Student(SQLModel, table=True):
    model_config = {"extra": "forbid"}
    student_id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    fullname: str = "NaN"
    department: str = "NaN"
    grade: int = -1
    gpa: float = -1.0
    year_of_entry: int | None = None
    class_id: int | None = Field(default=None, foreign_key="class.class_id")
    dept_id: int | None = Field(default=None, foreign_key="department.department_id")

class StudentUpdate(SQLModel):
    model_config = {"extra": "forbid"}
    fullname: str | None = None
    department: str | None = None
    grade: int | None = None
    gpa: float | None = None
    year_of_entry: int | None = None
    class_id: int | None = Field(default=None, foreign_key="class.class_id")
    dept_id: int | None = Field(default=None, foreign_key="department.department_id")
