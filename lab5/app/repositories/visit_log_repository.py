from typing import Optional, List

from .base_repository import Pagination

from .base_repository import BaseRepository, func
from ..models import VisitLog, User

class VisitLogsRepository(BaseRepository):
    model = VisitLog
    order_by = (VisitLog.created_at.desc(), VisitLog.user_id.asc(), VisitLog.id.desc())

    def get_by_id(self, visit_log_id: int) -> Optional[VisitLog]:
        return self._get_one(id=visit_log_id)

    def all(self, pagination: Pagination = None, sort: bool = False, **kwargs) -> List[VisitLog]:
        order_by = None
        if sort:
            order_by = self.order_by
        logs = self._get_all(pagination=pagination, order_by=order_by, **kwargs)
        return logs

    def create(self, path: str, user_id: int = None) -> VisitLog:
        visit_log = VisitLog(
            path=path,
            user_id=user_id
        )
        self.db_connector.session.add(visit_log)
        self.db_connector.session.commit()
        return visit_log

    def get_pages_visits_paged(self) -> tuple[Pagination, List[tuple]]:
        query = (
            self.db_connector.select(
                VisitLog.path,
                func.count(VisitLog.id).label('visit_count')
            )
            .group_by(VisitLog.path)
            .order_by(func.count(VisitLog.id).desc())
        )
        pagination = self._complex_query_pagination(query)
        return pagination, pagination.items

    def get_users_visits_paged(self) -> tuple[Pagination, List[tuple]]:
        query = (
            self.db_connector.select(
                func.coalesce(
                    func.concat(User.last_name, ' ', User.first_name, ' ', func.coalesce(User.middle_name, '')),
                    'Неаутентифицированный пользователь'
                ).label('full_name'),
                func.count(VisitLog.id).label('visit_count')
            )
            .outerjoin(User, VisitLog.user_id == User.id)
            .group_by(VisitLog.user_id)
            .order_by(func.count(VisitLog.id).desc())
        )
        pagination = self._complex_query_pagination(query)
        return pagination, pagination.items
