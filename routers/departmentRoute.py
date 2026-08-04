from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from sqlmodel import Session, select
from models.Department import Department, DepartmentPost, DepartmentUpdate
from models.User import UserRole
from auth.auth import require_role
from sql import get_session

router = APIRouter(
    prefix="/departments",
    tags=["Department"],
    dependencies=[Depends(require_role(UserRole.admin))]
)

session_deps = Annotated[Session, Depends(get_session)]

@router.get("/{department_id}")
def get_department(
    department_id: Annotated[int, Path()],
    session: session_deps
):
        returned_dept = session.get(Department, department_id)
        if not returned_dept:
            raise HTTPException(status_code=404, detail="Department not found")
        return returned_dept

@router.post("/")
def post_department(
    session: session_deps,
    department: Annotated[DepartmentPost, Body()]
):
        department_dict = department.model_dump()
        db_department = Department(**department_dict)

        session.add(db_department)
        session.commit()
        session.refresh(db_department)
        
        return db_department

@router.patch("/{id}")
def update_department(
    session: session_deps,
    id: Annotated[int, Path()], 
    update_inf: Annotated[DepartmentUpdate, Body()]):
        searched_dept = session.get(Department, id)
        if not searched_dept:
            raise HTTPException(status_code=404, detail="Department to update not found!")

        update_inf_dict = update_inf.model_dump(exclude_unset=True)

        for key, value in update_inf_dict.items():
            setattr(searched_dept, key, value)

        session.add(searched_dept)
        session.commit()

        session.refresh(searched_dept)

        return {"status": "Department has been updated", "Department": searched_dept}

@router.delete("/{department_id}", tags=["Department"])
def delete_department(
    department_id: Annotated[int, Path()],
    session: Annotated[Session, Depends(get_session)]
):  
    searched_dept = session.get(Department, department_id)
    if not searched_dept:
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department doesn't exist!")
    
    session.delete(searched_dept)
    session.commit()

    return {"result": f"succesfully deleted {searched_dept}"}

@router.get("/", tags=["Department"])
def get_all_departments(
      session: Annotated[Session, Depends(get_session)],
):
    all_departments = session.exec(select(Department)).all()
    if not all_departments: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Departments Found!")
    return all_departments