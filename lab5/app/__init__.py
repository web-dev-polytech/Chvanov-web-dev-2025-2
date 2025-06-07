from functools import wraps

from flask import Flask, render_template, request
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

    from .users import bp, index
    app.register_blueprint(bp)

    from .visit_logs import bp
    app.register_blueprint(bp)
    
    app.errorhandler(SQLAlchemyError)(database_error)
    app.route('/', endpoint='index')(index)

    from .repositories import get_repository
    from flask_login import current_user
    import re
    visit_log_repository = get_repository('visit_logs')
    @app.before_request
    def log_visit():
        excluded_patterns = [
            r'^/static/',
            r'/delete$',
            r'/logout$',
            r'\.ico$',
            r'\.css$',
            r'\.js$',
            r'\.png$|\.jpg$|\.gif$'
        ]
        if request.method != 'GET':
            return
        for pattern in excluded_patterns:
            if re.search(pattern, request.path):
                return
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
        visit_log_repository.create(request.path, user_id)

    return app
