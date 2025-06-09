from .base_policy import BasePolicy, authentication_required

class VisitLogsPolicy(BasePolicy):
    @authentication_required
    def show_all(self):
        return self._allow_only('admin')

    @authentication_required
    def show_statistics_page(self):
        return self._allow_only('admin')