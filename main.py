from contextlib import asynccontextmanager
from datetime import datetime
import logging
from typing import Annotated, Optional
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, Session, delete, select
from models.StudentLectureLink import StudentLectureLink
from models import Class, Department, Lecture, Student, Teacher, User
from models.Department import DepartmentUpdate, DepartmentPost
from models.Teacher import TeacherPost, TeacherUpdate
from models.User import UserCreate, UserRole
from auth.auth import get_password_hash, verify_password, create_access_token, get_current_user, require_role
from sql import start_db

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
            lect3 = Lecture(name="Judaism 101", lecture_code="JUD101", lecture_dept=3, lecture_session=1)

            session.add(lect1)  
            session.add(lect2)
            session.add(lect3)
            session.commit()
            logging.info("Lectures added to the database!")

def create_classes(engine: Engine):
    with Session(engine) as session:
        existing_classes = session.get(Class, 1)
        if not existing_classes:
            class1 = Class(class_name="F123")
            class2 = Class(class_name="A440")

            session.add(class1)
            session.add(class2)
            logging.info("Classes added to the database!")
            pass


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
    yield

# Attach the lifespan to your FastAPI app
app = FastAPI(lifespan=lifespan)
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

@app.get("/students/{student_id}", tags=["Student"])
async def get_student(
    admin_user: admin_user_deps, #DONT DELETE, ITS USED
    student_id: int, 
    q: Annotated[str | None, Query(lt=100)] = None,
    ):
    with Session(engine_global) as session:
        student = session.get(Student, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
            
        student_dict = student.model_dump()
        if q:
            return {**student_dict, "q": q}
        return student_dict

@app.get("/students/", tags=["Student"])
async def get_all_students(
    admin_user: admin_user_deps
):
    with Session(engine_global) as session:
        all_students = session.exec(select(Student)).all()
        if all_students == None:
            raise HTTPException(status_code=404, detail="No student found!")
        return all_students


@app.post("/students/", tags=["Student"])
async def create_student(student: Student,admin_user: admin_user_deps):
    with Session(engine_global) as session:
        session.add(student)
        session.commit()
        session.refresh(student)
        return student

@app.patch("/students/{student_id}", tags=["Student"])
async def update_student(student_id: int, student: Annotated[Student, Body(embed=True)], admin_user: admin_user_deps):
    results = {"student_id": student_id, "student": student}
    return results

@app.delete("/students/{student_id}", tags=["Student"])
async def delete_student(student_id: Annotated[int, Path()], admin_user: admin_user_deps):
    with Session(engine_global) as session:
        # statement = select(Student).where(Student.student_id == student_id)
        # results = session.exec(statement)
        student = session.get(Student, student_id)

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        print("Student: ", student)

        session.delete(student)
        session.commit()
        
        return {"ok": True, "message": f"Student {student_id} successfully deleted"}

@app.get("/teachers/{teacher_id}", tags=["Teacher"])
def get_teacher(
    admin_user: admin_user_deps,
    teacher_id: Annotated[int, Path(title="ID of teacher")]
    ):
    with Session(engine_global) as session:
        searched_teacher = session.get(Teacher, teacher_id)
        if not searched_teacher:
            raise HTTPException(status_code=404, detail="Teacher Not found")
        return searched_teacher

@app.get("/teachers/", tags=["Teacher"])
def get_all_teachers(
    admin_user: admin_user_deps,
):
    with Session(engine_global) as session:
        all_teachers: Annotated[dict[Teacher], Body(embed=True)] = session.exec(select(Teacher)).all()
        if not all_teachers or all_teachers == []:
            raise HTTPException(status_code=404, detail="Teacher Not Found!")
        return all_teachers
    

@app.post("/teachers/", tags=["Teacher"])
def post_teacher(
    admin_user: admin_user_deps,
    teacher: Annotated[TeacherPost, Body()]
) :
    with Session(engine_global) as session:
        teacher_dict = teacher.model_dump()

        TeacherPost_to_Teacher: Teacher = Teacher(**teacher_dict)

        session.add(TeacherPost_to_Teacher)
        session.commit()
        session.refresh(TeacherPost_to_Teacher)
        return TeacherPost_to_Teacher

@app.patch("/teachers/{teacher_id}", tags=["Teacher"])
def update_teacher(
    admin_user: admin_user_deps,
    teacher_id: Annotated[int, Path(description="Used for partially updating info on desired teacher")],
    update_info: Annotated[TeacherUpdate, Body(title="Partially Update Teacher")] ):

    with Session(engine_global) as session:
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

@app.delete("/teachers/{teacher_id}", tags=["Teacher"])
async def delete_teacher(
    admin_user: admin_user_deps,
    teacher_id: Annotated[int , Path(description="Teacher ID to be deleted",
    title="Teacher ID")]
):
    with Session(engine_global) as session:
        delete_teach = session.get(Teacher, teacher_id)
        if not delete_teach:
            raise HTTPException(status_code=404, detail="Teacher not found!")
        session.delete(delete_teach)
        session.commit()
        # session.refresh(delete_teach)
        return {"status":f"succesfully slimed the teach! slimed teach: {delete_teach}"}

@app.get("/departments/{department_id}",tags=["Department"])
def get_department(
    admin_user: admin_user_deps,
    department_id: Annotated[int, Path()]
):
    with Session(engine_global) as session:
        returned_dept = session.get(Department, department_id)
        if not returned_dept:
            raise HTTPException(status_code=404, detail="Department not found")
        return returned_dept

@app.post("/departments/", tags=["Department"])
def post_department(
    admin_user: admin_user_deps,
    department: Annotated[DepartmentPost, Body()]
):
    with Session(engine_global) as session:
        department_dict = department.model_dump()
        db_department = Department(**department_dict)

        session.add(db_department)
        session.commit()
        session.refresh(db_department)
        
        return db_department

@app.patch("/departments/{id}", tags=["Department"])
def update_department(
    admin_user: admin_user_deps,
    id: Annotated[int, Path()], 
    update_inf: Annotated[DepartmentUpdate, Body()]):
    with Session(engine_global) as session:
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


@app.get("/TESTING/",tags=["//TESTING//"])
def anything_goes_around_here_nowadays():

    with Session(engine_global) as session:
        return session.exec(select(User)).all()