from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from typing import Optional, List

from ..models import User

class UserRepository:
    def __init__(self, db_connector: SQLAlchemy):
        self.db_connector = db_connector

    def _get_one(self, model, **kwargs) -> Optional[User]:
        query = self.db_connector.select(model).filter_by(**kwargs)
        return self.db_connector.session.execute(query).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self._get_one(User, id=user_id)

    def get_by_login(self, login: str) -> Optional[User]:
        return self._get_one(User, login=login)

    def all(self) -> List[User]:
        query = self.db_connector.select(User).options(joinedload(User.role))
        return self.db_connector.session.execute(query).scalars().all()

    def create(self, login: str, password: str, first_name: str, middle_name: Optional[str], last_name: str, role_id: int) -> User:
        user = User(
            login=login,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            role_id=role_id
        )
        user.set_password(password)
        self.db_connector.session.add(user)
        self.db_connector.session.commit()
        return user

    def update(self, user_id: int, first_name: str, middle_name: Optional[str], last_name: str, role_id: int) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.role_id = role_id
            self.db_connector.session.commit()
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db_connector.session.delete(user)
            self.db_connector.session.commit()
            return True
        return False

    def check_password(self, login: str, password: str) -> bool:
        user = self.get_by_login(login)
        if user:
            return user.check_password(password)
        return False

    def validate_user(self, login: str, password: str) -> bool:
        user = self.get_by_login(login)
        if user and user.check_password(password):
            return user
        return None

    def update_password(self, user_id: int, new_password: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if user:
            user.set_password(new_password)
            self.db_connector.session.commit()
        return user
