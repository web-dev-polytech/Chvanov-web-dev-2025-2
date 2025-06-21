from flask import Blueprint, request, render_template, url_for, flash, redirect, session
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from functools import wraps

from .policies.events_policy import EventsPolicy

from ..repositories import get_repository

policies = {
    'events': EventsPolicy,
}

bp = Blueprint('auth', __name__, url_prefix='/auth')

user_repository = get_repository('users')

def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для доступа к данной странице необходимо пройти процедуру аутентификации.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    return user_repository.get_user_by_id(user_id)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        if login and password:
            user = user_repository.get_user_by_login(login)
            if user and user.check_password(password):
                login_user(user)
                flash('Вы успешно аутентифицированы.', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('main.index'))
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('auth/login.html')

@bp.route('/logout', methods=['GET'])
def logout():
    was_authenticated = True if current_user.is_authenticated else False
    logout_user()
    if was_authenticated:
        flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('main.index'))

def user_allowed(resource, action, **kwargs):
    policy = policies[resource](**kwargs)
    return getattr(policy, action, lambda: False)()

def check_rights(resource, action):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not user_allowed(resource, action, **kwargs):
                flash('У вас недостаточно прав для выполнения данного действия', 'warning')
                return redirect(url_for('main.index'))
            return function(*args, **kwargs)
        return wrapper
    return decorator
