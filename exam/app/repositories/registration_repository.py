from typing import List, Optional
from datetime import datetime
from .base_repository import BaseRepository
from ..models import Registration, RegistrationStatus

class RegistrationRepository(BaseRepository):
    model = Registration
    default_order_by = (Registration.date.desc(),)
    
    def get_user_registrations(self, user_id: int) -> List[Registration]:
        """Получить все регистрации пользователя"""
        return self.get_all(volunteer_id=user_id)
    
    def get_event_registrations(self, event_id: int, status: RegistrationStatus = None) -> List[Registration]:
        """Получить все регистрации на событие, опционально фильтровать по статусу"""
        filters = {'event_id': event_id}
        if status:
            filters['status'] = status
        return self.get_all(**filters)
    
    def get_user_event_registration(self, user_id: int, event_id: int) -> Optional[Registration]:
        """Получить регистрацию конкретного пользователя на конкретное событие"""
        registrations = self.get_all(volunteer_id=user_id, event_id=event_id)
        return registrations[0] if registrations else None
    
    def create_registration(self, event_id: int, volunteer_id: int, 
                          contact_info: str) -> Registration:
        """Создать новую регистрацию"""
        registration = self.create(
            event_id=event_id,
            volunteer_id=volunteer_id,
            contact_info=contact_info,
            date=datetime.now(),
            status=RegistrationStatus.PENDING
        )
        self.save()
        return registration
    
    def update_registration_status(self, registration: Registration, 
                                 status: RegistrationStatus) -> Registration:
        """Обновить статус регистрации"""
        updated_registration = self.update(registration, status=status)
        self.save()
        return updated_registration
    
    def get_pending_registrations(self) -> List[Registration]:
        """Получить все регистрации в статусе ожидания"""
        return self.get_all(status=RegistrationStatus.PENDING)
    
    def get_accepted_registrations_count(self, event_id: int) -> int:
        """Получить количество принятых регистраций для события"""
        accepted_registrations = self.get_event_registrations(
            event_id, RegistrationStatus.ACCEPTED
        )
        return len(accepted_registrations)
