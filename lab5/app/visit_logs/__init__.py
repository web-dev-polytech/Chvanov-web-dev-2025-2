from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for
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

@bp.route('/pages_visits')
@login_required
@check_rights('visit_logs', 'show_statistics_page')
def pages_visits():
    pagination, pages_visits = visit_log_repository.get_pages_visits_paged()
    return render_template('visit_logs/pages_visits.html',
                            pagination=pagination,
                            pages_visits=pages_visits)

@bp.route('/pages_visits/download')
@login_required
@check_rights('visit_logs', 'show_statistics_page')
def download_pages_visits():
    try:
        buffer, filename = visit_log_repository.export_table('pages_visits')
        return send_file(
            buffer, 
            as_attachment=True, 
            download_name=filename,
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f"Error generating CSV: {str(e)}", 'danger')
        return redirect(url_for('visit_logs.pages_visits'))

@bp.route('/users_visits')
@login_required
@check_rights('visit_logs', 'show_statistics_page')
def users_visits():
    pagination, users_visits = visit_log_repository.get_users_visits_paged()
    return render_template('visit_logs/users_visits.html',
                            pagination=pagination,
                            users_visits=users_visits)

@bp.route('/users_visits/download')
@login_required
@check_rights('visit_logs', 'show_statistics_page')
def download_users_visits():
    try:
        buffer, filename = visit_log_repository.export_table('users_visits')
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
    except Exception as e:
        flash(f"Error generating CSV: {str(e)}", 'danger')
        return redirect(url_for('visit_logs.users_visits'))
