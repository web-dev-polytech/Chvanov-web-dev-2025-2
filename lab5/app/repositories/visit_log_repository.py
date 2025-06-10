from typing import Optional, List

from .base_repository import Pagination, DataFrame, query

from .base_repository import BaseRepository, func
from ..models import VisitLog, User

class VisitLogsRepository(BaseRepository):
    model = VisitLog
    order_by = (VisitLog.created_at.desc(), VisitLog.user_id.asc(), VisitLog.id.desc())

    @property
    def _pages_visits_query(self) -> query:
        query = (
            self.db_connector.select(
                VisitLog.path,
                func.count(VisitLog.id).label('visit_count')
            )
            .group_by(VisitLog.path)
            .order_by(func.count(VisitLog.id).desc())
        )
        return query

    @property
    def _users_visits_query(self) -> query:
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
        return query

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
        pagination = self._complex_query_pagination(self._pages_visits_query)
        return pagination, pagination.items

    def get_users_visits_paged(self) -> tuple[Pagination, List[tuple]]:
        pagination = self._complex_query_pagination(self._users_visits_query)
        return pagination, pagination.items

    def export_table(self, statistic_name: str):
        if statistic_name == "pages_visits":
            query = self._pages_visits_query
            columns = ['Страница', 'Количество посещений']
        elif statistic_name == "users_visits":
            query = self._users_visits_query
            columns = ['Пользователь', 'Количество посещений']
        else:
            raise ValueError("Application doesn't have the representation for this statistic")
        table = self._get_table_pd(query, columns)
        buffered, filename = self._prepare_download_csv(table, statistic_name)
        return buffered, filename
