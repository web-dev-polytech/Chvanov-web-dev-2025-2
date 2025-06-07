from ..models import db

from .user_repository import UserRepository
from .role_repository import RoleRepository
from .visit_log_repository import VisitLogsRepository

from typing import Union

REPOSITORIES = {
    'users': UserRepository,
    'roles': RoleRepository,
    'visit_logs': VisitLogsRepository
}

def get_repository(resource: str) -> Union[UserRepository, RoleRepository, VisitLogsRepository]:
    if resource not in REPOSITORIES:
        raise ValueError(f"Repository '{resource}' not found. Available: {list(REPOSITORIES.keys())}")
    return REPOSITORIES[resource](db)
