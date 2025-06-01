import os
from typing import Optional, Union, List
from datetime import datetime
import sqlalchemy
from flask_login import UserMixin
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime, Text, Integer, MetaData

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class Role(Base):
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)
    description: Mapped[str] = mapped_column(Text)

    users: Mapped[List["User"]] = relationship("User", back_populates="role")

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(25), nullable=False)
    last_name: Mapped[str] = mapped_column(String(25), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(25), default=None, nullable=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=sqlalchemy.sql.func.now(), nullable=False)

    role_id: Mapped[int] = mapped_column(ForeignKey('roles.id'), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, login='{self.login}', first_name='{self.first_name}', last_name='{self.last_name}')"

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
