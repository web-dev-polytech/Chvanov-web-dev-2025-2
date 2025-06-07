from flask import Blueprint, request, render_template, url_for, flash, redirect, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from functools import wraps
from .checkers import check_password

from .policies.users_policy import UsersPolicy
from .policies.visit_logs_policy import VisitLogsPolicy

from ..repositories import get_repository

policies = {
    'users': UsersPolicy,
    'visit_logs': VisitLogsPolicy
}

bp = Blueprint('auth', __name__, url_prefix='/auth')

user_repository = get_repository('users')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходима аутентификация'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return user
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        next_page = request.args.get('next')
        if next_page:
            session['next'] = next_page
    if request.method == "POST":
        login = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        user = user_repository.validate_user(login, password)
        if user is not None:
            login_user(user, remember=remember_me)
            flash('Вы успешно аутентифицированы', 'success')
            next_page = session.pop('next', None)
            if not next_page or next_page == '/':
                next_page = url_for('index')
            return redirect(next_page)
        flash('Неправильный логин или пароль', 'danger')
    return render_template('auth/auth.html')

@bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        flash('Вы вышли из аккаунта', 'info')
    logout_user()
    return redirect(url_for('index'))

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    errors = {}
    fields = ('old_password', 'new_password', 'confirm_password')
    form_passwords = { field: request.form.get(field) or None for field in fields }
    if request.method == "POST":
        if user_repository.validate_user(current_user.login, form_passwords['old_password']) is None:
            errors['old_password'] = 'Старый пароль неверен'
        try: check_password(form_passwords['new_password'])
        except ValueError as e:
            errors['new_password'] = str(e)
        if form_passwords['new_password'] != form_passwords['confirm_password']:
            errors['confirm_password'] = 'Пароли не совпадают'
        if not errors:
            user_repository.update_password(current_user.get_id(), form_passwords['new_password'])
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('index'))
    return render_template('auth/change_password.html', form_passwords=form_passwords, errors=errors)

def user_allowed(resource, action, **kwargs):
    policy = policies[resource](**kwargs)
    return getattr(policy, action, lambda: False)()

def check_rights(resource, action):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not user_allowed(resource, action, **kwargs):
                flash('У вас недостаточно прав для доступа к данной странице.', 'warning')
                return redirect(url_for('users.index'))
            return function(*args, **kwargs)
        return wrapper
    return decorator
