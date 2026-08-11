from sqlmodel import SQLModel, Field

class StudentLectureLink(SQLModel, table=True):
    # Both fields are Primary Keys, creating a "Composite Primary Key"
    # This ensures a student cannot be enrolled in the exact same lecture twice
    student_id: int | None = Field(default=None, foreign_key="student.id", primary_key=True, ondelete="CASCADE")
    lecture_id: int | None = Field(default=None, foreign_key="lecture.id", primary_key=True, ondelete="CASCADE")