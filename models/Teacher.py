from typing import TYPE_CHECKING, Annotated, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    # 2. Add the dot (.) to tell Python to look in the same folder
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
    class_id: int | None = Field(default=None, description="Store as comma-separated, or use a Relationship table")
    dept_id: int | None = Field(default=None, foreign_key="department.id")
    user_id: int | None = Field(default=None, foreign_key="user.id", unique=True)
    orcid_id: str | None = None
    user: Optional["User"] = Relationship(back_populates="teacher_profile")
    department: Optional["Department"] = Relationship(back_populates="teachers")
    lectures: list["Lecture"] = Relationship(back_populates="lecturer")

class TeacherPost(SQLModel):
    model_config = {"extra": "forbid"}
    fullname: str
    class_id: int | None = Field(default=None, description="Store as comma-separated, or use a Relationship table")
    dept_id: int | None = Field(default=None)
    orcid_id: str | None = None

class TeacherUpdate(SQLModel):
    model_config = {"extra": "forbid"}
    fullname: str | None = Field(default=None)
    class_id: int | None = Field(default=None, description="Store as comma-separated, or use a Relationship table")
    dept_id: int | None = Field(default=None)
    orcid_id: str | None = None