from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    """Academic Department model."""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)

    instructors = relationship("Instructor", back_populates="department", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")


class Instructor(Base):
    """Faculty Instructor model."""
    __tablename__ = "instructors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    office = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    department = relationship("Department", back_populates="instructors")
    courses = relationship("Course", back_populates="instructor")


class Prerequisite(Base):
    """Prerequisite association table mapping dependent courses to required courses."""
    __tablename__ = "prerequisites"

    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    prerequisite_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)


class Course(Base):
    """University Course model."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructors.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    department = relationship("Department", back_populates="courses")
    instructor = relationship("Instructor", back_populates="courses")

    # Courses required prior to taking this course
    prerequisites = relationship(
        "Course",
        secondary="prerequisites",
        primaryjoin="Course.id == Prerequisite.course_id",
        secondaryjoin="Course.id == Prerequisite.prerequisite_id",
        backref="required_for"
    )
