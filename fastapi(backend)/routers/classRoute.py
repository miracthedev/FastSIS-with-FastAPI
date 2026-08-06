from typing import Annotated

from sqlmodel import Session, select

from models.User import UserRole
from auth.auth import require_role
from models import Class
from models.Class import Buildings, ClassPost, ClassUpdate
from fastapi import Body, Depends, Path, status, HTTPException, APIRouter

from sql import get_session

router = APIRouter(
    prefix="/classes",
    tags=["Class"],
    dependencies=[Depends(require_role(UserRole.admin))],
)

session_deps = Annotated[Session, Depends(get_session)]

@router.get("/")
def get_all_classes(
    session: session_deps
):
    db_classes = session.exec(select(Class)).all()
    if not db_classes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Class Exists!")

    return db_classes

@router.get("/{class_id}")
def get_class(
    class_id: Annotated[int, Path()],
    session: session_deps
):
    searched_class = session.get(Class, class_id)
    return searched_class

@router.delete("/{class_id}")
def delete_class(
    class_id: Annotated[int, Path()],
    session: Annotated[Session, Depends(get_session)]
):
    db_session = session.get(Class, class_id)
    if not db_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class Not Found!")

    db_session_dict = db_session.model_dump()

    session.delete(db_session)
    session.commit()
    
    return db_session_dict

@router.post("/")
def post_class(
    session: session_deps,
    postClassInfo: Annotated[ClassPost, Body()]
):
    post_class_dict = postClassInfo.model_dump()

    db_class = Class(**post_class_dict)

    print(db_class)
    
    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    return_class = db_class.model_dump()
    return return_class

@router.patch("/{class_id}")
def update_class(
    session: session_deps,
    class_id: Annotated[int, Path()],
    class_update: Annotated[ClassUpdate, Body()]
):
    db_class = session.get(Class, class_id)
    if not db_class:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class Not Found!")

    class_update_dict = class_update.model_dump(exclude_unset=True)


    for k,v in class_update_dict.items():
        setattr(db_class, k, v)

    session.add(db_class)
    session.commit()
    session.refresh(db_class)

    return db_class