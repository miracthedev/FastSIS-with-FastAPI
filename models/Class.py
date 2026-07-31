from sqlmodel import Relationship, SQLModel, Field
from typing import TYPE_CHECKING, Annotated

#TODO: use RELATIONSHIP() instead of Field()

if TYPE_CHECKING:
    from models import Student, Teacher, Class, Department

class Class(SQLModel, table=True):
    id: Annotated[int, Field(..., title="Class ID",description="ID of the class", primary_key=True)]
    class_name: Annotated[str, Field("UndefClass", title="Class name", description="Used for naming the class")]
    students: list["Student"] = Relationship(back_populates="student_class")