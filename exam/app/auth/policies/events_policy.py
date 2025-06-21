from .base_policy import BasePolicy, authentication_required

class EventsPolicy(BasePolicy):
    def show(self):
        return True

    @authentication_required
    def edit(self):
        return self._allow_set(['модератор', 'администратор'])

    @authentication_required
    def delete(self):
        return self._allow_only('администратор')
    
    @authentication_required
    def create(self):
        return self._allow_only('администратор')
