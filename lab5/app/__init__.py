from flask import Flask
from flask_migrate import Migrate

from .models import db

migrate = Migrate()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile('config.py', silent=False)

    if test_config:
        app.config.from_mapping(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .auth import bp, login_manager
    app.register_blueprint(bp)
    login_manager.init_app(app)

    from . import users
    app.register_blueprint(users.bp)
    app.route('/', endpoint='index')(users.index)

    return app
