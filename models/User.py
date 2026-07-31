from enum import Enum
import re
from typing import TYPE_CHECKING, Annotated, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr, field_validator
from sqlmodel import UUID, Field, Relationship, SQLModel
import uuid # For generating the default value
from uuid import UUID # For the type hint itself

if TYPE_CHECKING:
    from .Student import Student
    from .Teacher import Teacher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserRole(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    pass


class User(SQLModel, table=True):
    id: Annotated[int, Field(primary_key=True)]
    email: Annotated[EmailStr, Field(unique=True, index=True)]
    hashed_password: str
    role: UserRole = Field(default=UserRole.student)

    student_profile: Optional["Student"] = Relationship(back_populates="user")
    teacher_profile: Optional["Teacher"] = Relationship(back_populates="user")

class UserCreate(SQLModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.student

    # 4. Strict Password Validation
    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        return value
