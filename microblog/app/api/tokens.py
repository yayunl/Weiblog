from flask import jsonify, g
from .. import db
from . import bp
from .auth import basic_auth


@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    # Generate a token for the authorized user
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})


@bp.route('/tokens', methods=['DELETE'])
def revoke_token():
    g.current_user.revoke_token()
    db.session.commit()
    return "",204