from flask import render_template, request
from .. import db
from ..errors import bp
from ..api.errors import error_response as api_error_response


def wants_json_response():
    # If json rates higher than html, it returns josn. Otherwise, it returns HTML.
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error():
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error():
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500