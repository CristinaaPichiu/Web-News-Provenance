from flask import request, jsonify, Blueprint

from api.services.email_service import generate_reset_token, send_reset_email

email_blueprint = Blueprint('email', __name__)


@email_blueprint.route('/request-reset-email', methods=['POST'])
def request_reset_email():
    email = request.json['email']
    token = generate_reset_token(email)
    reset_url = f"http://localhost:4200/set-password?token={token}"
    send_reset_email(email, reset_url)

    return jsonify({
        'message': 'Please check your email for the password reset link',
        'reset_token': token,  # Returnează token-ul în răspuns
        'reset_url': reset_url  # De asemenea, returnează linkul complet
    }), 200
