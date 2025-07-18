from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from .repositories import get_repository
from .auth import check_rights
from .auth.checkers import check_login, check_password

user_repository = get_repository('users')
role_repository = get_repository('roles')

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/')
def index():
    sort = True
    pagination = user_repository.get_pagination_info(sort=sort)
    users = user_repository.all(pagination=pagination, sort=sort)
    return render_template('users/index.html',
                            pagination=pagination,
                            users=users)

@bp.route('/<int:user_id>')
@login_required
@check_rights('users', 'show')
def show(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))
    return render_template('users/show.html', 
                            user_data=user, 
                            user_role=user.role.name)

@bp.route('/create', methods=['POST', 'GET'])
@login_required
@check_rights('users', 'create')
def create():
    user_data, errors = {}, {}
    if request.method == 'POST':
        fields = ('login', 'password', 'first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}
        try: 
            check_login(user_data['login'])
        except ValueError as e:
            errors['login'] = str(e)
        try: 
            check_password(user_data['password'])
        except ValueError as e:
            errors['password'] = str(e)
        if errors:
            return render_template('users/create.html', 
                                    user_data=user_data, 
                                    roles=role_repository.all(), 
                                    errors=errors)
        try:
            user_repository.create(**user_data)
            flash('Учетная запись успешно создана', 'success')
            return redirect(url_for('users.index'))
        except IntegrityError as e:
            user_repository.rollback()
            flash('Пользователь с таким логином уже существует', 'danger')
        except SQLAlchemyError as e:
            user_repository.rollback()
            flash('Произошла ошибка при создании записи. Попробуйте снова', 'danger')
    return render_template('users/create.html', 
                            user_data=user_data, 
                            roles=role_repository.all(), 
                            errors=errors)

@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
@check_rights('users', 'delete')
def delete(user_id):
    try:
        if user_repository.delete(user_id):
            flash('Учетная запись успешно удалена', 'success')
        else:
            flash('Пользователь не найден', 'warning')
    except SQLAlchemyError:
        user_repository.rollback()
        flash('Произошла ошибка при удалении записи', 'danger')
    return redirect(url_for('users.index'))

@bp.route('/<int:user_id>/edit', methods=['POST', 'GET'])
@login_required
@check_rights('users', 'edit')
def edit(user_id):
    user = user_repository.get_by_id(user_id)
    if user is None:
        flash('Пользователя нет в базе данных', 'danger')
        return redirect(url_for('users.index'))
    if request.method == 'POST':
        fields = ('first_name', 'middle_name', 'last_name', 'role_id')
        user_data = {field: request.form.get(field) or None for field in fields}
        try:
            user_repository.update(user_id, **user_data)
            flash('Учетная запись успешно изменена', 'success')
            return redirect(url_for('users.index'))
        except SQLAlchemyError:
            user_repository.rollback()
            flash('Произошла ошибка при изменении записи', 'danger')
            for field in fields:
                setattr(user, field, user_data[field])
    return render_template('users/edit.html',
                            user_data=user,
                            roles=role_repository.all())