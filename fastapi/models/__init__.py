# models/__init__.py

from .Student import Student
from .Teacher import Teacher, TeacherPost, TeacherUpdate
from .Department import Department, DepartmentPost, DepartmentUpdate
from .Lecture import Lecture, LectureUpdate, LecturePost
from .Class import Class
from .User import User, UserRole, UserCreate
from .StudentLectureLink import StudentLectureLink