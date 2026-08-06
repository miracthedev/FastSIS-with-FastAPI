from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING, Annotated
from enum import Enum
#TODO: use RELATIONSHIP() instead of Field()

if TYPE_CHECKING:
    from models import Student, Teacher, Class, Department, Lecture

class Buildings(str, Enum):
    ambarch = "Ambarch"
    celik_bina = "Çelik Bina"
    fabrika = "Fabrika Binası"
    lab = "Lab Binası"
    default = "UndefBuilding"

class Class(SQLModel, table=True):
    id: Annotated[int, Field(..., title="Class ID",description="ID of the class", primary_key=True)]
    name: Annotated[str, Field(default="UndefClass", title="Class name", description="Used for naming the class")]
    resides_in: Buildings = Buildings.default
    floor: Annotated[int, Field(default=0, ge=-5, le=5)]
    students: list["Student"] = Relationship(back_populates="student_class")
    lectures: list["Lecture"] = Relationship(back_populates="classes")

class ClassPost(SQLModel):
    name: Annotated[str, Field(title="Class name", description="Used for naming the class")]
    resides_in: Buildings = Buildings.default
    floor: Annotated[int, Field(default=0, ge=-5, le=5)]

class ClassUpdate(SQLModel):
    name: Annotated[str | None, Field(default=None)]
    resides_in: Annotated[Buildings, Field(default=None)]
    floor: Annotated[int, Field(default=0, ge=-5, le=5)]