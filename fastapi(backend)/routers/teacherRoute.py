from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy import select
from sqlmodel import Session

from models.Teacher import Teacher, TeacherPost, TeacherUpdate
from models.User import UserRole
from auth.auth import require_role
from sql import get_session

router = APIRouter(
    prefix="/teachers",
    tags=["Teacher"],
    dependencies=[Depends(require_role(UserRole.admin))]
)


@router.get("/{teacher_id}", tags=["Teacher"])
def get_teacher(
    teacher_id: Annotated[int, Path(title="ID of teacher")],
    session: Annotated[Session, Depends(get_session)],
    ):
    searched_teacher = session.get(Teacher, teacher_id)
    if not searched_teacher:
        raise HTTPException(status_code=404, detail="Teacher Not found")
    return searched_teacher

@router.get("/", tags=["Teacher"])
def get_all_teachers(
    session: Annotated[Session, Depends(get_session)],
):
    all_teachers: Annotated[dict[Teacher], Body(embed=True)] = session.exec(select(Teacher)).all()
    if not all_teachers or all_teachers == []:
        raise HTTPException(status_code=404, detail="Teacher Not Found!")
    return all_teachers
    

@router.post("/", tags=["Teacher"])
def post_teacher(
    teacher: Annotated[TeacherPost, Body()],
    session: Annotated[Session, Depends(get_session)],
) :
        teacher_dict = teacher.model_dump()

        TeacherPost_to_Teacher: Teacher = Teacher(**teacher_dict)

        session.add(TeacherPost_to_Teacher)
        session.commit()
        session.refresh(TeacherPost_to_Teacher)
        return TeacherPost_to_Teacher

@router.patch("/{teacher_id}", tags=["Teacher"])
def update_teacher(
    session: Annotated[Session, Depends(get_session)],
    teacher_id: Annotated[int, Path(description="Used for partially updating info on desired teacher")],
    update_info: Annotated[TeacherUpdate, Body(title="Partially Update Teacher")] ):

        retrieved_teacher = session.get(Teacher, teacher_id)

        if not retrieved_teacher:
            raise HTTPException(status_code=404, detail="Teacher not found!")

        update_data = update_info.model_dump(exclude_unset=True)

        if not update_data:
            return {"status": "Nothing has been updated, input is empty"}

        for key, value in update_data.items():
            setattr(retrieved_teacher, key, value)

        session.add(retrieved_teacher)
        session.commit()

        session.refresh(retrieved_teacher)

        return {"status": "Teacher has been updated", "teacher": retrieved_teacher}

@router.delete("/{teacher_id}", tags=["Teacher"])
async def delete_teacher(
    session: Annotated[Session, Depends(get_session)],
    teacher_id: Annotated[int , Path(description="Teacher ID to be deleted",
    title="Teacher ID")]
):
        delete_teach = session.get(Teacher, teacher_id)
        if not delete_teach:
            raise HTTPException(status_code=404, detail="Teacher not found!")
        session.delete(delete_teach)
        session.commit()
        # session.refresh(delete_teach)
        return {"status":f"succesfully slimed the teach! slimed teach: {delete_teach}"}
