from decimal import Decimal

from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Annotated, Optional

from .StudentLectureLink import StudentLectureLink

model_config_dep = {"extra": "forbid"}

#TODO: use RELATIONSHIP() instead of Field()

if TYPE_CHECKING:
    from models import Student, Teacher, Class, Department

class Lecture(SQLModel, table=True):
    model_config = model_config_dep
    id : Annotated[int, Field(default=None, title="Lecture ID",description="ID of the Lecture", primary_key=True)]
    name : Annotated[str, Field(default="UndefLecture", title="Lecture name", description="Used for naming the Lecture")]
    lecture_code: Annotated[str, Field(max_length=20)]
    lecture_session: Annotated[int, Field(max_length=1, gt=0)]
    lecture_dept : Annotated[int | None, Field(default=None, title="Lecture's origin dept.", description="Used for declaring which department this class belongs to", foreign_key="department.id")]
    teacher_id: Annotated[int | None, Field(default=None, foreign_key="teacher.id", ondelete="CASCADE")]
    ects: int | None = Field(default=0, le=50, ge=0, )

    # Relationships
    department: Optional["Department"] = Relationship(back_populates="lectures")
    lecturer: Optional["Teacher"] = Relationship(back_populates="lectures")
    students: list["Student"] = Relationship(
        back_populates="lectures", 
        link_model=StudentLectureLink)

    # Field Validators
    @field_validator("lecture_code", mode="before") ## Mutates all letters to uppercase and saves it to db. 
    @classmethod
    def force_uppercase(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        return value


class LecturePost(SQLModel):
    model_config = model_config_dep
    lecture_name : Annotated[str, Field(title="Lecture name", description="Used for naming the Lecture")]
    lecture_dept : Annotated[int, Field(
        title="Lecture's origin dept.", 
        description="Used for declaring which department this class belongs to", 
        foreign_key="department.id")]

class LectureUpdate(SQLModel):
    model_config = model_config_dep
    lecture_name : Annotated[Optional[str], Field(title="Lecture name", description="Used for naming the Lecture")]
    lecture_dept : Annotated[Optional[int], Field(
        title="Lecture's origin dept.", 
        description="Used for declaring which department this class belongs to", 
        foreign_key="department.id")]