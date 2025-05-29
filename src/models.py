from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func, Text, Table, Column

from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

db = SQLAlchemy()


"""
    Esta es una relación de uno a uno
"""


class Parent(db.Model):
    __tablename__ = "parent"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)

    # la relación con el hijo (para poder raer cosas del hijo)
    child: Mapped["Child"] = relationship(
        back_populates="parent",  uselist=False)


class Child(db.Model):
    __tablename__ = "child"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[String] = mapped_column(String(80), nullable=True)
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("parent.id"), nullable=False, unique=True)

    # la relación con el padre (para poder raer cosas del padre)
    parent: Mapped["Parent"] = relationship(back_populates="child")


"""
    Esta es una relación de uno a muchos
"""


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    # la relación con los todos (para poder traer cosas de los todos)
    todos: Mapped[List["Todos"]] = relationship(back_populates="user")


class Todos(db.Model):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False)
    # la relación con el usuario (para poder traer cosas del usuario)
    user: Mapped["User"] = relationship(back_populates="todos")


"""
    Esta es la relación muchos a muchos
"""
association_table = Table(
    "association",
    db.metadata,
    Column("studen_id", ForeignKey("student.id"), primary_key=True),
    Column("course_id", ForeignKey("course.id"), primary_key=True)
)


class Student(db.Model):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    courses: Mapped[List["Course"]] = relationship(
        "Course",
        secondary=association_table,
        back_populates="students"
    )


class Course(db.Model):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    students: Mapped[List["Student"]] = relationship(
        "Student",
        secondary=association_table,
        back_populates="courses"
    )
