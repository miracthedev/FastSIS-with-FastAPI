import logging

from sqlalchemy import Engine
from sqlmodel import Field, SQLModel, Session, create_engine, select
from models import Class, Department, Lecture, Student, Teacher, User, UserRole
from models.Class import Buildings

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)
SQLModel.metadata.create_all(engine)

def start_db():
    return engine

def get_session():
    with Session(engine) as session:
        yield session

def create_dummy_datas(engine: Engine):

    create_students(engine)
    create_teachers(engine)
    create_lectures(engine)
    create_departments(engine)
    create_classes(engine)
    create_users(engine)

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
            session.commit()
            logging.info("Classes added to the database!")

def create_users(engine: Engine):
    with Session(engine) as session:
        statement = select(User).where(User.email == "mirac@gmail.com")
        existing_user = session.exec(statement).first()

        from auth.auth import get_password_hash
        
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