from flask_sqlalchemy import SQLAlchemy, query
from flask_sqlalchemy.extension import Pagination
from sqlalchemy import func, select
from typing import Optional, TypeVar, Type, List

T = TypeVar('T')

class BaseRepository:
    model: Type[T] = None
    order_by: tuple = None
    
    def __init__(self, db_connector: SQLAlchemy):
        self.db_connector = db_connector

    def _get_all_query(self, order_by = None, query = None, **kwargs) -> query:
        if query is None:
            query = self.db_connector.select(self.model).filter_by(**kwargs)
            if order_by:
                query = query.order_by(*order_by)
        return query

    def _get_one(self, **kwargs) -> Optional[T]:
        return self.db_connector.session.execute(self._get_all_query(order_by=None, **kwargs)).scalar_one_or_none()

    def _get_all(self, pagination: Pagination = None, order_by = None, **kwargs) -> List[Optional[T]]:
        if pagination is not None:
            return pagination.items
        return self.db_connector.session.execute(self._get_all_query(order_by=order_by, **kwargs)).scalars().all()

    def _complex_query_pagination(self, query: query) -> List:
        pagination = self.db_connector.paginate(query)
        all_items = self.db_connector.session.execute(query).all()
        items_dict = {row[0]: row[1] for row in all_items}
        items_paginated = []
        for item in pagination.items:
            if isinstance(item, str):
                item_key = item
            else:
                item_key = item[0] if hasattr(item, '__getitem__') else str(item)
            items_paginated.append((item_key, items_dict.get(item_key, 0)))
        pagination.items = items_paginated
        return pagination

    def get_pagination_info(self, sort: bool = False, query = None, **kwargs) -> Pagination:
        order_by = None
        if sort:
            order_by = self.order_by
        query = self._get_all_query(order_by=order_by, query=query, **kwargs)
        return self.db_connector.paginate(query)

    def rollback(self) -> None:
        self.db_connector.session.rollback()
