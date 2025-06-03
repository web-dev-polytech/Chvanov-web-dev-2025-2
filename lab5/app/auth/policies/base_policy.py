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
    def __init__(self):
        raise NotImplementedError

    def create(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def edit(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError
