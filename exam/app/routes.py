from flask import Blueprint, redirect, url_for, send_from_directory, abort, current_app
from .models import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return redirect(url_for('events.index'))

@bp.route('/images/<image_id>')
def image(image_id):
    if image_id is None:
        abort(404)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               image_id)
