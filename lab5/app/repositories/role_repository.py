from flask_sqlalchemy import SQLAlchemy
from typing import Optional, List

from ..models import Role

class RoleRepository:
    def __init__(self, db_connector: SQLAlchemy):
        self.db_connector = db_connector

    def get_by_id(self, role_id: int) -> Optional[Role]:
        query = self.db_connector.select(Role).filter_by(id=role_id)
        return self.db_connector.session.execute(query).scalar_one_or_none()

    def all(self) -> List[Role]:
        query = self.db_connector.select(Role)
        return self.db_connector.session.execute(query).scalars().all()