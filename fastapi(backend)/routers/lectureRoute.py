from sqlmodel import select
from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlmodel import Session
from models import Lecture, UserRole, LecturePost, LectureUpdate
from auth.auth import require_role
from sql import get_session
from fastapi import status

router = APIRouter(
    prefix="/lectures",
    tags=["Lecture"],
    dependencies=[Depends(require_role(UserRole.admin))]
)

@router.get("/")
def get_all_lectures(
    session: Annotated[Session, Depends(get_session)],
    q_name: str | None = Query(default=None)
):
    statement = select(Lecture)

    if q_name:
        q_name = q_name.upper()
        statement = statement.where(Lecture.lecture_code == q_name)

    searched_lectures = session.exec(statement).all()

    if not searched_lectures:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lecture exists!")
    
    return searched_lectures

@router.get("/{lecture_id}")
def get_lecture(
    lecture_id: Annotated[int, Path()],
    session: Annotated[Session, Depends(get_session)]
):
    searched_lecture: Lecture = session.get(Lecture, lecture_id)
    if not searched_lecture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture Not Found!")

    return searched_lecture

@router.post("/")
def create_lecture(
    session: Annotated[Session, Depends(get_session)],
    post_lecture: Annotated[LecturePost, Body()]
):
    post_lecture_dict = post_lecture.model_dump()

    created_lecture: Lecture = Lecture(**post_lecture_dict)
    
    session.add(created_lecture)
    session.commit()
    session.refresh(created_lecture)

    return created_lecture.model_dump()

@router.patch("/{lecture_id}")
def update_lecture(
    session: Annotated[Session, Depends(get_session)],
    update_lecture: Annotated[LectureUpdate, Body()],
    lecture_id: Annotated[int, Path()]
):
    searched_lecture = session.get(Lecture, lecture_id)
    # session.exec(select(Lecture).where(Lecture.id == searched_lecture.id)).first()
    if not searched_lecture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture Not Found!")

    upd_lecture_dict = update_lecture.model_dump(exclude_unset=True)

    for key, value in upd_lecture_dict.items():
        setattr(searched_lecture, key, value)
    
    session.add(searched_lecture)
    session.commit()
    session.refresh(searched_lecture)

    return searched_lecture

@router.delete("/{lecture_id}")
def delete_lecture(
    lecture_id: Annotated[int, Path()],
    session: Annotated[Session, Depends(get_session)]
):
    db_lecture = session.get(Lecture, lecture_id)

    if not db_lecture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecture Not Found!")

    session.delete(db_lecture)
    return db_lecture
'''
{
"lecture_name":"Yoga 101",
"":"",
"":""

}

'''