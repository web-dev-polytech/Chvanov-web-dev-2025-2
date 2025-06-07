from functools import wraps
from flask_login import current_user

def authentication_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return False
        return func(*args, **kwargs)
    return wrapper

class BasePolicy:
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')

    def get_page(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def edit(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def _allow_only(self, role: str) -> bool:
        return current_user.role.name == role

    def _admin_all_user_self(self) -> bool:
        if current_user.role.name == 'admin':
            return True
        if current_user.role.name == 'user':
            assert self.user_id is not None
            return current_user.id == self.user_id
        return False
