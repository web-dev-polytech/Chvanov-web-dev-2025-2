from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.extension import Pagination
from sqlalchemy import func, select

from typing import Optional, TypeVar, Type, List

T = TypeVar('T')

class BaseRepository:
    model: Type[T] = None
    default_order_by: tuple = None
    per_page: int = 10
    
    def __init__(self, db_connector: SQLAlchemy):
        self.db = db_connector

    def get_by_id(self, id: int) -> Optional[T]:
        return self.db.session.get(self.model, id)

    def get_all(self, order_by=None, **filters) -> List[T]:
        query = self.db.select(self.model).filter_by(**filters)
        
        if order_by:
            query = query.order_by(*order_by if isinstance(order_by, (list, tuple)) else [order_by])
        elif self.default_order_by:
            query = query.order_by(*self.default_order_by)
            
        return self.db.session.execute(query).scalars().all()

    def get_paginated(self, order_by=None, **filters) -> Pagination:
        query = self.db.select(self.model).filter_by(**filters)
        
        if order_by:
            query = query.order_by(*order_by if isinstance(order_by, (list, tuple)) else [order_by])
        elif self.default_order_by:
            query = query.order_by(*self.default_order_by)
            
        return self.db.paginate(query, per_page=self.per_page, error_out=False)

    def create(self, **data) -> T:
        obj = self.model(**data)
        self.db.session.add(obj)
        return obj

    def update(self, obj: T, **data) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

    def delete(self, obj: T) -> None:
        self.db.session.delete(obj)

    def save(self) -> None:
        self.db.session.commit()

    def rollback(self) -> None:
        self.db.session.rollback()
