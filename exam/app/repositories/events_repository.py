from datetime import datetime
from typing import List, Tuple
from flask_sqlalchemy.extension import Pagination

from .base_repository import BaseRepository
from ..models import Event

class EventRepository(BaseRepository):
    model = Event
    default_order_by = (Event.date.desc(),)
    per_page = 10

    def get_events_by_organizer(self, organizer_id: int) -> List[Event]:
        return self.get_all(organizer_id=organizer_id)

    def get_upcoming_events(self) -> Tuple[Pagination, List[Event]]:
        query = (
            self.db.select(Event)
            .filter(Event.date >= datetime.now())
            .order_by(*self.default_order_by)
        )
        pagination = self.db.paginate(query, per_page=self.per_page)
        return pagination, pagination.items

    def create_event(self, name: str, description: str, date: datetime, 
                    location: str, volunteer_required: int, image: str, 
                    organizer_id: int) -> Event:
        event = self.create(
            name=name,
            description=description,
            date=date,
            location=location,
            volunteer_required=volunteer_required,
            image=image,
            organizer_id=organizer_id
        )
        self.save()
        return event

    def update_event(self, event: Event, **data) -> Event:
        updated_event = self.update(event, **data)
        self.save()
        return updated_event

    def delete_event(self, event_id: int) -> None:
        event = self.get_by_id(event_id)
        self.delete(event)
        self.save()
        return True
