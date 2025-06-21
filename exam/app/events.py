import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
import markdown

from .repositories import get_repository
from .auth import check_rights
from .models import RegistrationStatus

user_repository = get_repository('users')
event_repository = get_repository('events')
registration_repository = get_repository('registrations')

bp = Blueprint('events', __name__, url_prefix='/events')

EVENT_PARAMS = [
    'name', 'description', 'date', 'location', 'volunteer_required', 'image'
]

def params():
    return { p: request.form.get(p) or None for p in EVENT_PARAMS }

@bp.route('/')
def index():
    pagination, events = event_repository.get_upcoming_events()
    return render_template('events/index.html',
                           pagination=pagination,
                           events=events)

@bp.route('/new')
@login_required
@check_rights('events', 'create')
def new():
    return render_template('events/new.html')

@bp.route('/create', methods=['POST'])
@login_required
@check_rights('events', 'create')
def create():
    f = request.files.get('image')
    img_filename = 'default.jpg'
    event = None
    
    try:
        if f and f.filename:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in f.filename and f.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                filename = secure_filename(f.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, unique_filename)
                f.save(file_path)
                img_filename = unique_filename
            else:
                flash('Недопустимый формат файла. Разрешены: PNG, JPG, JPEG, GIF', 'danger')
                return render_template('events/new.html')
        
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre']
        allowed_attributes = {'a': ['href'], 'code': ['class']}
        clean_description = bleach.clean(
            request.form.get('description', ''), 
            tags=allowed_tags, 
            attributes=allowed_attributes
        )
        
        from datetime import datetime
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        event = event_repository.create_event(
            name=request.form.get('name'),
            description=clean_description,
            date=date,
            location=request.form.get('location'),
            volunteer_required=int(request.form.get('volunteer_required', 0)),
            image=img_filename,
            organizer_id=current_user.id
        )
        
    except IntegrityError as err:
        event_repository.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/new.html', event=event)
    except Exception as err:
        event_repository.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/new.html', event=event)
        
    flash(f'Мероприятие "{event.name}" было успешно создано!', 'success')
    return redirect(url_for('events.show', event_id=event.id))

@bp.route('/<int:event_id>/')
@check_rights('events', 'show')
def show(event_id):
    event = event_repository.get_by_id(event_id)
    if not event:
        flash('Такого мероприятия не существует', 'danger')
        return redirect(url_for('events.index'))
    
    # Преобразуем Markdown в HTML
    event.description_html = markdown.markdown(event.description)
    
    # Получаем регистрации
    accepted_registrations = []
    pending_registrations = []
    user_registration = None
    
    if current_user.is_authenticated:
        # Получаем регистрацию текущего пользователя
        user_registration = registration_repository.get_user_event_registration(
            current_user.id, event_id
        )
        
        # Получаем списки регистраций для админов и модераторов
        if hasattr(current_user, 'role') and current_user.role.name in ['Администратор', 'Модератор']:
            accepted_registrations = registration_repository.get_event_registrations(
                event_id, RegistrationStatus.ACCEPTED
            )
            # Сортируем по дате регистрации (по убыванию)
            accepted_registrations.sort(key=lambda x: x.date, reverse=True)
            
            # Для модераторов - получаем ожидающие регистрации
            if current_user.role.name == 'Модератор':
                pending_registrations = registration_repository.get_event_registrations(
                    event_id, RegistrationStatus.PENDING
                )
                pending_registrations.sort(key=lambda x: x.date, reverse=True)
    
    return render_template('events/show.html', 
                           event=event,
                           accepted_registrations=accepted_registrations,
                           pending_registrations=pending_registrations,
                           user_registration=user_registration)

@bp.route('/<int:event_id>/edit')
@login_required
@check_rights('events', 'edit')
def edit(event_id):
    event = event_repository.get_by_id(event_id)
    if not event:
        flash('Такого мероприятия не существует', 'danger')
        return redirect(url_for('events.index'))
    return render_template('events/edit.html', event=event)

@bp.route('/<int:event_id>/update', methods=['POST'])
@login_required
@check_rights('events', 'edit')
def update(event_id):
    event = event_repository.get_by_id(event_id)
    if not event:
        flash('Такого мероприятия не существует', 'danger')
        return redirect(url_for('events.index'))
    
    try:
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre']
        allowed_attributes = {'a': ['href'], 'code': ['class']}
        clean_description = bleach.clean(
            request.form.get('description', ''), 
            tags=allowed_tags, 
            attributes=allowed_attributes
        )
        
        from datetime import datetime
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        event_repository.update_event(event,
            name=request.form.get('name'),
            description=clean_description,
            date=date,
            location=request.form.get('location'),
            volunteer_required=int(request.form.get('volunteer_required', 0))
        )
        
    except IntegrityError as err:
        event_repository.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/edit.html', event=event)
    except Exception as err:
        event_repository.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/edit.html', event=event)
        
    flash(f'Мероприятие "{event.name}" было успешно обновлено!', 'success')
    return redirect(url_for('events.show', event_id=event.id))

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
@check_rights('events', 'delete')
def delete(event_id):
    event = event_repository.get_by_id(event_id)
    if not event:
        flash('Мероприятие не найдено', 'warning')
        return redirect(url_for('events.index'))
    
    try:
        event_repository.delete_event(event)
        flash('Мероприятие успешно удалено', 'success')
    except Exception as err:
        event_repository.rollback()
        flash('Произошла ошибка при удалении мероприятия', 'danger')
    
    return redirect(url_for('events.index'))

@bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    """Регистрация на мероприятие"""
    event = event_repository.get_by_id(event_id)
    if not event:
        flash('Мероприятие не найдено', 'danger')
        return redirect(url_for('events.index'))
    
    # Проверяем, что пользователь не зарегистрирован ранее
    existing_registration = registration_repository.get_user_event_registration(
        current_user.id, event_id
    )
    if existing_registration:
        flash('Вы уже зарегистрированы на это мероприятие', 'warning')
        return redirect(url_for('events.show', event_id=event_id))
    
    contact_info = request.form.get('contact_info', '').strip()
    if not contact_info:
        flash('Контактная информация обязательна', 'danger')
        return redirect(url_for('events.show', event_id=event_id))
    
    try:
        registration_repository.create_registration(
            event_id=event_id,
            volunteer_id=current_user.id,
            contact_info=contact_info
        )
        flash('Заявка на регистрацию отправлена!', 'success')
    except Exception as e:
        registration_repository.rollback()
        flash('Произошла ошибка при регистрации', 'danger')
    
    return redirect(url_for('events.show', event_id=event_id))

@bp.route('/<int:event_id>/approve_registration/<int:volunteer_id>', methods=['POST'])
@login_required
@check_rights('events', 'moderate')
def approve_registration(event_id, volunteer_id):
    """Принятие заявки на регистрацию"""
    registration = registration_repository.get_user_event_registration(volunteer_id, event_id)
    if not registration:
        flash('Регистрация не найдена', 'danger')
        return redirect(url_for('events.show', event_id=event_id))
    
    try:
        # Принимаем заявку
        registration_repository.update_registration_status(registration, RegistrationStatus.ACCEPTED)
        
        # Проверяем, не набралось ли достаточно волонтёров
        event = event_repository.get_by_id(event_id)
        accepted_count = registration_repository.get_accepted_registrations_count(event_id)
        
        if accepted_count >= event.volunteer_required:
            # Отклоняем остальные ожидающие заявки
            pending_registrations = registration_repository.get_event_registrations(
                event_id, RegistrationStatus.PENDING
            )
            for pending_reg in pending_registrations:
                registration_repository.update_registration_status(pending_reg, RegistrationStatus.REJECTED)
            
            flash(f'Заявка принята! Набор волонтёров завершён ({accepted_count}/{event.volunteer_required})', 'success')
        else:
            flash('Заявка принята!', 'success')
            
    except Exception as e:
        registration_repository.rollback()
        flash('Произошла ошибка при обработке заявки', 'danger')
    
    return redirect(url_for('events.show', event_id=event_id))

@bp.route('/<int:event_id>/reject_registration/<int:volunteer_id>', methods=['POST'])
@login_required
@check_rights('events', 'moderate')
def reject_registration(event_id, volunteer_id):
    """Отклонение заявки на регистрацию"""
    registration = registration_repository.get_user_event_registration(volunteer_id, event_id)
    if not registration:
        flash('Регистрация не найдена', 'danger')
        return redirect(url_for('events.show', event_id=event_id))
    
    try:
        registration_repository.update_registration_status(registration, RegistrationStatus.REJECTED)
        flash('Заявка отклонена', 'info')
    except Exception as e:
        registration_repository.rollback()
        flash('Произошла ошибка при обработке заявки', 'danger')
    
    return redirect(url_for('events.show', event_id=event_id))
