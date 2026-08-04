from contextlib import asynccontextmanager
import logging
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import Engine
from sqlmodel import  Session, delete, select
from models import Class, Department, Lecture, Student, Teacher, User
from models.Class import Buildings
from models.User import UserCreate, UserRole
from auth.auth import get_password_hash, verify_password, create_access_token, get_current_user, require_role
from sql import start_db

# Routers
from routers import departmentRoute, lectureRoute, studentRoute, teacherRoute

# Global engine
engine_global = start_db()

def create_teachers(engine: Engine):
    with Session(engine) as session:
        existing_teacher = session.get(Teacher, 1)
        if not existing_teacher:
            teacher1 = Teacher(fullname="hoca1")
            teacher2 = Teacher(fullname="hocacav")
            teacher3 = Teacher(fullname="234")
            teacher4 = Teacher(fullname="1 1 1")

            session.add(teacher1)
            session.add(teacher2)
            session.add(teacher3)
            session.add(teacher4)
            session.commit()
            logging.info("teachers added to the database")

def create_students(engine: Engine):
    with Session(engine) as session:
        existing_student = session.get(Student, 1)
        if not existing_student:
            student1 = Student(fullname="mirazozalp", dept_id=1, grade=4, gpa=2.70, year_of_entry=2022)
            student2 = Student(fullname="fractali", dept_id=1, grade=4, gpa=3.99, year_of_entry=2022)
            student3 = Student(fullname="avc", dept_id=2, grade=9532, gpa=4.1, year_of_entry=1970)
            student4 = Student(fullname="xyz", dept_id=2, grade=23, gpa=1.1, year_of_entry=1984)

            session.add(student1)  
            session.add(student2)
            session.add(student3)
            session.add(student4)
            session.commit()
            logging.info("Students added to the database!")

def create_departments(engine: Engine):
    with Session(engine) as session:
        existing_depts = session.get(Department, 1)
        if not existing_depts:
            dept1 = Department(name="Computer Engineering")
            dept2 = Department(name="Electrical Engineering")
            dept3 = Department(name="Industrial Engineering")

            session.add(dept1)  
            session.add(dept2)
            session.add(dept3)
            session.commit()
            logging.info("Departments added to the database!")

def create_lectures(engine: Engine):
    with Session(engine) as session:
        existing_lectures = session.get(Lecture, 1)
        if not existing_lectures:
            lect1 = Lecture(name="Discrete Math", lecture_code="MATH206", lecture_dept=1, lecture_session=1)
            lect2 = Lecture(name="Object Orianted Programming", lecture_code="COMP201", lecture_dept=1, lecture_session=1)
            lect3 = Lecture(name="Yoga 101", lecture_code="YOGA101", lecture_dept=3, lecture_session=1)

            session.add(lect1)  
            session.add(lect2)
            session.add(lect3)
            session.commit()
            logging.info("Lectures added to the database!")

def create_classes(engine: Engine):
    with Session(engine) as session:
        existing_classes = session.get(Class, 1)
        if not existing_classes:
            class1 = Class(name="F123", resides_in=Buildings.ambarch, floor=2)
            class2 = Class(name="A440", resides_in=Buildings.celik_bina, floor=3)

            session.add(class1)
            session.add(class2)
            logging.info("Classes added to the database!")
            pass

def create_users(engine: Engine):
    with Session(engine) as session:
        statement = select(User).where(User.email == "mirac@gmail.com")
        existing_user = session.exec(statement).first()
        
        if not existing_user:
            hashed_pw = get_password_hash("Mirac2026")
            new_user = User(
                email="mirac@gmail.com", 
                hashed_password=hashed_pw, 
                role=UserRole.admin
            )
            session.add(new_user)
            print("Admin user created!")

            hashed_pw = get_password_hash("Dilara2026")
            new_user = User(
                email="dilara@gmail.com", 
                hashed_password=hashed_pw, 
                role=UserRole.student
            )
            session.add(new_user)

            hashed_pw = get_password_hash("Ali2026")
            new_user = User(
                email="ali@gmail.com", 
                hashed_password=hashed_pw, 
                role=UserRole.teacher
            )
            session.add(new_user)
            print("Teacher user created!")


            session.commit()
            print("Student user created!")

logging.info("Confirmation that things are working.")

#########################################
# DELVE DEEP ON THIS !!!!
# Define the Lifespan event to trigger creation on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_students(engine_global)
    create_teachers(engine_global)
    create_lectures(engine_global)
    create_departments(engine_global)
    create_classes(engine_global)
    create_users(engine_global)
    yield

# Attach the lifespan to your FastAPI app
app = FastAPI(lifespan=lifespan)

app.include_router(studentRoute.router)
app.include_router(teacherRoute.router)
app.include_router(departmentRoute.router)
app.include_router(lectureRoute.router)
#########################################



def getter_all():
    with Session(engine_global) as session:
        students = session.exec(select(Student)).all()
        teachers = session.exec(select(Teacher)).all()
        classes = session.exec(select(Class)).all()
        depts = session.exec(select(Department)).all()
        lectures = session.exec(select(Lecture)).all()

        if not students and not teachers and not classes and not depts and not lectures:
            raise HTTPException(status_code=404, detail="The database is completely empty.")

        return {
            "students": students,
            "teachers": teachers,
            "departments": depts,
            "classes": classes,
            "lectures": lectures
        }

getter_all_deps = Annotated[dict, Depends(getter_all)]

admin_user_deps = Annotated[str, Depends(require_role(UserRole.admin))]
student_user_deps = Annotated[str, Depends(require_role(UserRole.student))]
teacher_user_deps = Annotated[str, Depends(require_role(UserRole.teacher))]

@app.get("/", tags=["General"])
async def get_all_info(get_all: getter_all_deps, admin_user: admin_user_deps):
    return get_all

@app.get("/me/profile", tags=["Profile"])
def get_my_profile(current_user: Annotated[User, Depends(get_current_user)]):
    # Because of the 1:1 relationship, SQLAlchemy fetches the exact profile!
    if current_user.role == UserRole.student:
        return current_user.student_profile
        
    elif current_user.role == UserRole.teacher:
        return current_user.teacher_profile
        
    return {"message": "Admin users don't have academic profiles."}

@app.post("/users/register", tags=["Authentication"])
def register_user(
    user_in: UserCreate,
    # admin_user: admin_user_deps
):
    with Session(engine_global) as session:
        # 1. Check if the email is already taken
        existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 2. Hash the securely validated password
        hashed_pw = get_password_hash(user_in.password)
        
        # 3. Create the Database model
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_pw,
            role=user_in.role
        )
        
        # 4. Save to the database
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        # Safely return the user (FastAPI will hide the hashed_password 
        # if you use a response_model, but for now we just return a dictionary)
        return {"id": db_user.id, "email": db_user.email, "role": db_user.role}

@app.post("/token", tags=["Authentication"])
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    with Session(engine_global) as session:
        # Query the User table by email (OAuth2 uses the 'username' field to pass the email)
        user = session.exec(select(User).where(User.email == form_data.username)).first()

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate the token using the role!
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        return {"access_token": access_token, "token_type": "bearer"}

@app.delete("/", tags=["☢️"])
def WIPE_OUT(
    get_all: getter_all_deps,
    admin_user: admin_user_deps #DONT DELETE, ITS USED
):
    if (get_all != None):
        with Session(engine_global) as session:
            session.exec(delete(Student))
            session.exec(delete(Teacher))
            session.exec(delete(Class))
            session.exec(delete(Department))
            session.exec(delete(Lecture))

            #BOOM!!!
            session.commit()

            return{"result": "☢️'d database"}

@app.get("/TESTING/",tags=["//TESTING//"])
def anything_goes_around_here_nowadays():

    with Session(engine_global) as session:
        return session.exec(select(User)).all()