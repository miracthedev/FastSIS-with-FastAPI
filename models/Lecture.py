from sqlmodel import SQLModel, Field
from typing import Annotated

class Lecture(SQLModel, table=True):
    model_config = {"extra": "forbid"}
    lecture_id : Annotated[int, Field(default=None, title="Lecture ID",description="ID of the Lecture", primary_key=True)]
    lecture_name : Annotated[str, Field("UndefLecture", title="Lecture name", description="Used for naming the Lecture")]
    lecture_dept : Annotated[int, Field(default=None, title="Lecture's origin dept.", description="Used for declaring which department this class belongs to", foreign_key="department.department_id")]
