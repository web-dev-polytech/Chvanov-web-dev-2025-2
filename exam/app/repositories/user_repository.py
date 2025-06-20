from typing import Optional
from .base_repository import BaseRepository
from ..models import User

class UserRepository(BaseRepository):
    model = User
    default_order_by = (User.login, User.last_name, User.first_name)

    def get_user_by_id(self, id: int) -> Optional[User]:
        users = self.get_all(id=id)
        return users[0] if users else None
    
    def get_user_by_login(self, login: str) -> Optional[User]:
        users = self.get_all(login=login)
        return users[0] if users else None
    
    def get_users_by_role(self, role_id: int):
        return self.get_all(role_id=role_id)
    
    def create_user(self, login: str, password_hash: str, first_name: str, 
                   last_name: str, role_id: int, middle_name: str = None) -> User:
        user = self.create(
            login=login,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            role_id=role_id
        )
        self.save()
        return user
