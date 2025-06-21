from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from .models import db
from .repositories import get_repository
from .auth import check_rights

user_repository = get_repository('users')
event_repository = get_repository('events')

bp = Blueprint('events', __name__, url_prefix='/events')

EVENT_PARAMS = [
    'name', 'description', 'date', 'location', 'volunteer_required', 'image'
]

def params():
    return { p: request.form.get(p) or None for p in EVENT_PARAMS }

@bp.route('/')
def index():
    pagination, events = event_repository.get_current_and_future_events()
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
        # Обработка загрузки файла
        if f and f.filename:
            import os
            import uuid
            from werkzeug.utils import secure_filename
            
            # Проверяем расширение файла
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in f.filename and f.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                # Генерируем безопасное имя файла
                filename = secure_filename(f.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                # Создаем директорию если не существует
                upload_dir = os.path.join('app', 'static', 'images')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Сохраняем файл
                file_path = os.path.join(upload_dir, unique_filename)
                f.save(file_path)
                img_filename = unique_filename
            else:
                flash('Недопустимый формат файла. Разрешены: PNG, JPG, JPEG, GIF', 'danger')
                return render_template('events/new.html')
        
        # Санитизация описания
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre']
        allowed_attributes = {'a': ['href'], 'code': ['class']}
        clean_description = bleach.clean(
            request.form.get('description', ''), 
            tags=allowed_tags, 
            attributes=allowed_attributes
        )
        
        # Преобразование даты
        from datetime import datetime
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        # Создание события
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
        db.session.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/new.html', event=event)
    except Exception as err:
        db.session.rollback()
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
    
    return render_template('events/show.html', event=event)

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
        # Санитизация описания
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre']
        allowed_attributes = {'a': ['href'], 'code': ['class']}
        clean_description = bleach.clean(
            request.form.get('description', ''), 
            tags=allowed_tags, 
            attributes=allowed_attributes
        )
        
        # Преобразование даты
        from datetime import datetime
        date_str = request.form.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        
        # Обновление события
        event_repository.update_event(event,
            name=request.form.get('name'),
            description=clean_description,
            date=date,
            location=request.form.get('location'),
            volunteer_required=int(request.form.get('volunteer_required', 0))
        )
        
    except IntegrityError as err:
        db.session.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/edit.html', event=event)
    except Exception as err:
        db.session.rollback()
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
        db.session.rollback()
        flash('Произошла ошибка при удалении мероприятия', 'danger')
    
    return redirect(url_for('events.index'))

user_repository = get_repository('users')
event_repository = get_repository('events')

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
def index():
    pagination, events = event_repository.get_upcoming_events()
    return render_template('events/index.html',
                           pagination=pagination,
                           events=events)

@bp.route('/new')
@check_rights('events', 'create')
@login_required
def new():
    return render_template('events/new.html')

@bp.route('/create', methods=['POST'])
@login_required
@check_rights('events', 'create')
def create():
    try:
        # Получаем данные из формы
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        location = request.form.get('location', '').strip()
        volunteer_required = request.form.get('volunteer_required', '0')
        
        # Валидация
        if not all([name, description, date_str, location, volunteer_required]):
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('events/new.html')
        
        # Санитизация описания с помощью bleach
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre']
        allowed_attributes = {'a': ['href'], 'code': ['class']}
        clean_description = bleach.clean(description, tags=allowed_tags, attributes=allowed_attributes)
        
        # Преобразуем дату
        from datetime import datetime
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Неверный формат даты', 'danger')
            return render_template('events/new.html')
        
        # Обработка загрузки файла
        image_filename = 'default.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                import os
                import uuid
                from werkzeug.utils import secure_filename
                
                # Проверяем расширение файла
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # Генерируем безопасное имя файла
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    
                    # Создаем директорию если не существует
                    upload_dir = os.path.join('app', 'static', 'images')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Сохраняем файл
                    file_path = os.path.join(upload_dir, unique_filename)
                    file.save(file_path)
                    image_filename = unique_filename
                else:
                    flash('Недопустимый формат файла. Разрешены: PNG, JPG, JPEG, GIF', 'danger')
                    return render_template('events/new.html')
        
        # Создаем событие
        from flask_login import current_user
        event = event_repository.create_event(
            name=name,
            description=clean_description,
            date=date,
            location=location,
            volunteer_required=int(volunteer_required),
            image=image_filename,
            organizer_id=current_user.id
        )
        
        flash('Мероприятие успешно создано!', 'success')
        return redirect(url_for('events.show', event_id=event.id))
        
    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        event_repository.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/new.html')
            image=image,
            organizer_id=current_user.id
        )
        
        flash('Событие успешно создано!', 'success')
        return redirect(url_for('events.show', event_id=event.id))
        
    except Exception as e:
        flash(f'Ошибка при создании события: {str(e)}', 'danger')
        return redirect(url_for('events.new'))
#         users = user_repository.get_all_users()
#         return render_template('courses/new.html',
#                             categories=categories,
#                             users=users,
#                             course=course)
#     flash(f'Курс {course.name} был успешно добавлен!', 'success')
#     return redirect(url_for('courses.index'))

@bp.route('/<int:event_id>/')
@check_rights('events', 'show')
def show(event_id):
    event = event_repository.get_by_id(event_id)
    if not event:
        flash('Такого мероприятия не существует', 'danger')
        return redirect(url_for('main.index'))
    return render_template('events/show.html', event=event)

@bp.route('/<int:event_id>/edit')
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
        # Получаем данные из формы
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        location = request.form.get('location', '').strip()
        volunteer_required = request.form.get('volunteer_required', '0')
        
        # Валидация
        if not all([name, description, date_str, location, volunteer_required]):
            flash('Все поля обязательны для заполнения', 'danger')
            return render_template('events/edit.html', event=event)
        
        # Санитизация описания с помощью bleach
        import bleach
        allowed_tags = ['p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                       'ul', 'ol', 'li', 'blockquote', 'a', 'code', 'pre']
        allowed_attributes = {'a': ['href'], 'code': ['class']}
        clean_description = bleach.clean(description, tags=allowed_tags, attributes=allowed_attributes)
        
        # Преобразуем дату
        from datetime import datetime
        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Неверный формат даты', 'danger')
            return render_template('events/edit.html', event=event)
        
        # Обновляем событие
        event_repository.update_event(event,
            name=name,
            description=clean_description,
            date=date,
            location=location,
            volunteer_required=int(volunteer_required)
        )
        
        flash('Мероприятие успешно обновлено!', 'success')
        return redirect(url_for('events.show', event_id=event.id))
        
    except Exception as e:
        # Откатываем транзакцию в случае ошибки
        event_repository.rollback()
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        return render_template('events/edit.html', event=event)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
@check_rights('events', 'delete')
def delete(event_id):
    try:
        if event_repository.delete_event(event_id):
            flash('Мероприятие успешно удалено', 'success')
        else:
            flash('Мероприятие не найдено', 'warning')
    except SQLAlchemyError:
        user_repository.rollback()
        flash('Произошла ошибка при удалении записи', 'danger')
    return redirect(url_for('main.index'))
