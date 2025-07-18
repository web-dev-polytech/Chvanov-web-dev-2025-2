from flask import Flask
from flask_migrate import Migrate
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from .models import db
from .auth import bp as auth_bp, init_login_manager
from .courses import bp as courses_bp
from .routes import bp as main_bp

def handle_sqlalchemy_error(err):
    error_msg = ('Возникла ошибка при подключении к базе данных. '
                 'Повторите попытку позже.')
    return f'{error_msg} (Подробнее: {err})', 500

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py')

    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate = Migrate(app, db)

    init_login_manager(app)

    app.jinja_env.globals['current_user'] = current_user

    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(main_bp)
    app.errorhandler(SQLAlchemyError)(handle_sqlalchemy_error)

    return app