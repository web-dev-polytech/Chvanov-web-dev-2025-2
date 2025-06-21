from ..models import db

from .user_repository import UserRepository
from .events_repository import EventRepository
from .registration_repository import RegistrationRepository

from typing import Union

REPOSITORIES = {
    'users': UserRepository,
    'events': EventRepository,
    'registrations': RegistrationRepository,
}

def get_repository(resource: str) -> Union[UserRepository, EventRepository, RegistrationRepository]:
    if resource not in REPOSITORIES:
        raise ValueError(f"Repository '{resource}' not found. Available: {list(REPOSITORIES.keys())}")
    return REPOSITORIES[resource](db)
