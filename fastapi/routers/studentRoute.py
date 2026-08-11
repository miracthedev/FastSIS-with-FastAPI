from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body, status
from sqlmodel import Session, select

from sql import get_session
from models.Student import Student
from auth.auth import require_role
from models.User import UserRole

# 1. Lock down EVERY route in this file to Admins only
router = APIRouter(
    prefix="/students",
    tags=["Student"],
    dependencies=[Depends(require_role(UserRole.admin))]
)

@router.get("/{student_id}")
async def get_student(
    student_id: int, 
    session: Annotated[Session, Depends(get_session)],
    q: Annotated[str | None, Query(lt=100)] = None
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    student_dict = student.model_dump()
    if q:
        return {**student_dict, "q": q}
    return student_dict

@router.get("/")
async def get_all_students(session: Annotated[Session, Depends(get_session)]):
    all_students = session.exec(select(Student)).all()
    if not all_students:
        raise HTTPException(status_code=404, detail="No student found!")
    return all_students

@router.post("/")
async def create_student(
    student: Student,
    session: Annotated[Session, Depends(get_session)]
):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@router.patch("/{student_id}")
async def update_student(
    student_id: int, 
    update_student: Annotated[Student, Body(embed=True)],
    session: Annotated[Session, Depends(get_session)]
):
    searched_student = session.get(Student, student_id)
    if not searched_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student doesn't exist!")

    searched_student_dict = searched_student.model_dump()

    update_student_dict = update_student.model_dump(exclude_unset=True)

    for k,v in update_student_dict:
        setattr(searched_student_dict, k, v)

    return_student = Student(**searched_student_dict)

    return {"result":"Student Updated Succesfully!", "updated_student":f"{return_student}"}

    '''
    searched_student_dict = {
        "fullname":"adanali irfo",
        "gano":"3.1",
        "dept":"Computer Science"
    }

    update_student_dict = {
        "fullname":"urfali iytem",
        "gano":null
    }
    '''

@router.delete("/{student_id}")
async def delete_student(
    
    student_id: Annotated[int, Path()],
    session: Annotated[Session, Depends(get_session)]
):
    student = session.get(Student, student_id)

    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    session.delete(student)
    session.commit()
    
    return {"ok": True, "message": f"Student {student_id} successfully deleted"}