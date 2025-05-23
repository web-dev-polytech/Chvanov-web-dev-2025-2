from flask import Blueprint, request, render_template, url_for, flash, redirect, session
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required

from .repositories import UserRepository
from .utils import check_password
from . import db

user_repository = UserRepository(db)

bp = Blueprint('auth', __name__, url_prefix='/auth')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Для доступа к запрашиваемой странице необходима аутентификация'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

@login_manager.user_loader
def load_user(user_id):
    user = user_repository.get_by_id(user_id)
    if user is not None:
        return User(user['id'], user['login'])
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
        user = user_repository.get_by_login_and_password(login, password)
        if user is not None:
            login_user(User(user['id'], user['login']), remember=remember_me)
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
        if not user_repository.check_password(current_user.login, form_passwords['old_password']):
            errors['old_password'] = 'Старый пароль неверен'
        try: check_password(form_passwords['new_password'])
        except ValueError as e:
            errors['new_password'] = str(e)
            return render_template('auth/change_password.html', form_passwords=form_passwords, errors=errors)
        if form_passwords['new_password'] != form_passwords['confirm_password']:
            errors['confirm_password'] = 'Пароли не совпадают'
        if not errors:
            user_repository.update_password(current_user.get_id(), form_passwords['new_password'])
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('index'))
    return render_template('auth/change_password.html', form_passwords=form_passwords, errors=errors)
