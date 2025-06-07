from .base_policy import BasePolicy, authentication_required

class UsersPolicy(BasePolicy):
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

