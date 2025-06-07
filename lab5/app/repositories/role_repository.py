from typing import Optional, List

from .base_repository import BaseRepository
from ..models import Role

class RoleRepository(BaseRepository):
    model = Role
    
    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self._get_one(Role, id=role_id)

    def all(self) -> List[Role]:
        return self._get_all()
