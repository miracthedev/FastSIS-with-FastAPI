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

class Department(SQLModel, table=True):
    # department_id: UUID | None = None
    department_id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field( default_factory=datetime.now)
    department_name: str | None = None
    teachers: list["Teacher"] = Relationship(back_populates="department")   
