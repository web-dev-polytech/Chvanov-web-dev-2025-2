from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..repositories import get_repository
from ..auth import check_rights, user_allowed

visit_log_repository = get_repository('visit_logs')

bp = Blueprint('visit_logs', __name__, url_prefix='/visit_logs')

@bp.route('/')
@login_required
def index():
    params = {}
    if not user_allowed('visit_logs', 'show_all'):
        params['user_id'] = current_user.id
    sort = True
    pagination = visit_log_repository.get_pagination_info(sort=sort, **params)
    logs = visit_log_repository.all(pagination=pagination, sort=sort, **params)
    return render_template('visit_logs/index.html',
                            pagination=pagination,
                            logs=logs)
