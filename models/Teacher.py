from typing import TYPE_CHECKING, Annotated, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .Department import Department
    from .Lecture import Lecture
    from .User import User

#TODO: use RELATIONSHIP() instead of Field()

class Teacher(SQLModel, table=True):
    model_config = {"extra": "forbid"}
    
    # teacher_id: UUID | None =  None
    id: int | None =  Field(default=None, primary_key=True)
    fullname: str | None = Field(default="HocaHocaoglu")
    created_at: datetime = Field(default_factory=datetime.now)
    dept_id: int | None = Field(default=None, foreign_key="department.id")
    user_id: int | None = Field(default=None, foreign_key="user.id", unique=True)
    lecture_id: int | None = Field(default=None, foreign_key="lecture.id")
    orcid_id: str | None = None
    user: Optional["User"] = Relationship(back_populates="teacher_profile")
    department: Optional["Department"] = Relationship(back_populates="teachers")
    lectures: list["Lecture"] = Relationship(
        back_populates="lecturer", 
        sa_relationship_kwargs={
            "foreign_keys": "[Lecture.teacher_id]" 
        })

class TeacherPost(SQLModel):
    model_config = {"extra": "forbid"}
    fullname: str
    dept_id: int | None = Field(default=None)
    lecture_id: int | None = Field(default=None, foreign_key="lecture.id")
    orcid_id: str | None = None

class TeacherUpdate(SQLModel):
    model_config = {"extra": "forbid"}
    fullname: str | None = Field(default=None)
    dept_id: int | None = Field(default=None)
    lecture_id: int | None = Field(default=None, foreign_key="lecture.id")
    orcid_id: str | None = None