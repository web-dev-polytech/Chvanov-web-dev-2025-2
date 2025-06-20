from typing import Optional, List
from datetime import datetime
import enum
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, DateTime, MetaData, Enum

class Base(DeclarativeBase):
  metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class RegistrationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Event(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    volunteer_required: Mapped[int] = mapped_column(nullable=False)
    image: Mapped[str] = mapped_column(String(100), nullable=False)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    organizer: Mapped["User"] = relationship(back_populates="organized_events")
    registrations: Mapped[List["Registration"]] = relationship(back_populates="event")

    @property
    def volunteer_registered(self):
        accepted_registrations = list(filter(lambda registration: registration.status == RegistrationStatus.accepted, self.registrations))
        return len(accepted_registrations)
    
    @property
    def status(self):
        if self.volunteer_registered < self.volunteer_required:
            return "✅ Идёт набор волонтёров"
        return "❌ Регистрация закрыта"

    def __repr__(self):
        return '<Event %r>' % self.name

class Registration(Base):
    __tablename__ = 'registrations'

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)
    volunteer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    contact_info: Mapped[str] = mapped_column(String(120), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    status: Mapped[RegistrationStatus] = mapped_column(
        Enum(RegistrationStatus),
        default=RegistrationStatus.pending,
        nullable=False
    )

    event: Mapped["Event"] = relationship(back_populates="registrations")
    volunteer: Mapped["User"] = relationship(back_populates="registrations")

    def __repr__(self):
        return f'<Registration {self.volunteer_id} -> {self.event_id} ({self.status.value})>'

class User(Base, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    role: Mapped["Role"] = relationship(back_populates="users")
    registrations: Mapped[List["Registration"]] = relationship(back_populates="volunteer")
    organized_events: Mapped[List["Event"]] = relationship(back_populates="organizer")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def __repr__(self):
        return '<User %r>' % self.login

class Role(Base):
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return '<Role %r>' % self.name 
