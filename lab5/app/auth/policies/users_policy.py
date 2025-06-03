from multiprocessing import AuthenticationError
from flask_login import current_user
from ...repositories import get_repository
from .base_policy import BasePolicy, authentication_required

class UsersPolicy(BasePolicy):
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')

    @authentication_required
    def create(self):
        return self._allow_only('admin')

    @authentication_required
    def show(self):
        return self._admin_all_user_self()

    @authentication_required  
    def edit(self):
        return self._admin_all_user_self()

    @authentication_required
    def delete(self):
        return self._allow_only('admin')

    @authentication_required
    def switch_role(self):
        return self._allow_only('admin')

    def _allow_only(self, role: str):
        return current_user.role.name == role

    def _admin_all_user_self(self):
        if current_user.role.name == 'admin':
            return True
        if current_user.role.name == 'user':

            assert self.user_id is not None
            return current_user.id == self.user_id
        return False
