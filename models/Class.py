from sqlmodel import SQLModel, Field
from typing import Annotated

class Class(SQLModel, table=True):
    class_id: Annotated[int, Field(..., title="Class ID",description="ID of the class", primary_key=True)]
    class_name: Annotated[str, Field("UndefClass", title="Class name", description="Used for naming the class")]
    