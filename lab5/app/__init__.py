from flask import Flask, render_template
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError

from .models import db

migrate = Migrate()

def database_error(error):
    db.session.rollback()
    return render_template('errors/database_error.html', error=error), 500

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)

    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .auth import bp, login_manager, user_allowed
    app.register_blueprint(bp)
    login_manager.init_app(app)
    app.jinja_env.globals['user_allowed'] = user_allowed

    from . import users
    app.register_blueprint(users.bp)

    app.errorhandler(SQLAlchemyError)(database_error)
    app.route('/', endpoint='index')(users.index)

    return app
