from flask import Blueprint
from controllers.auth_controller import register, login, verify_token
from utils.auth import require_auth

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register_route():
    if request.method == 'OPTIONS':
        return '', 200
    return register()

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login_route():
    if request.method == 'OPTIONS':
        return '', 200
    return login()

@auth_bp.route('/verify', methods=['GET', 'OPTIONS'])
@require_auth
def verify_route():
    if request.method == 'OPTIONS':
        return '', 200
    return verify_token()