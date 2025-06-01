from app.models import db

from .user_repository import UserRepository
from .role_repository import RoleRepository

from typing import Union

REPOSITORIES = {
    'users': UserRepository,
    'roles': RoleRepository
}

def get_repository(resource: str) -> Union[UserRepository, RoleRepository]:
    if resource not in REPOSITORIES:
        raise ValueError(f"Repository '{resource}' not found. Available: {list(REPOSITORIES.keys())}")
    return REPOSITORIES[resource](db)
