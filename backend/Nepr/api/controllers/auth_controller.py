import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from itsdangerous import URLSafeTimedSerializer
from flask import current_app as app

from api.services.email_service import send_welcome_email
from databases.db_postgresql_conn import connect
from api.services.auth_service import get_user_by_email, create_user, authenticate_user

auth_blueprint = Blueprint('auth', __name__)

from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token


def verify_reset_token(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=app.config['SECURITY_PASSWORD_SALT'], max_age=3600)  # Token expiră în 1 oră
        return email
    except:
        return False

@auth_blueprint.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    session, _ = connect()
    email = verify_reset_token(token)

    if not email:
        return jsonify({'message': 'Invalid or expired token'}), 400

    user = get_user_by_email(session, email)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_password = request.json.get('new_password')
    try:
        user.set_password(new_password)  # Folosește metoda pentru a seta parola corect
        session.commit()
        return jsonify({'message': 'Password has been reset successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'message': str(e)}), 500
    finally:
        session.close()



@auth_blueprint.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200


@auth_blueprint.route('/register', methods=['POST'])
def register():
    session, _ = connect()
    email = request.json.get('email')
    password = request.json.get('password')
    first_name = request.json.get('first_name', '')
    last_name = request.json.get('last_name', '')

    existing_user = get_user_by_email(session, email)
    if existing_user:
        return jsonify({"message": "Email already in use"}), 409
    try:
        user = create_user(session, email, password, first_name, last_name)
        session.commit()
        try:
            send_welcome_email(email, first_name)
        except Exception as e:
            logging.error(f"Failed to send welcome email: {str(e)}")
            session.delete(user)
            session.commit()
            return jsonify({"message": "Failed to send welcome email, registration rolled back"}), 500

        # Dacă totul a mers bine, întoarce succes
        access_token = create_access_token(identity=email)
        return jsonify({"message": "User registered successfully", "access_token": access_token}), 201

    except Exception as e:
        session.rollback()
        return jsonify({"message": "Failed to register user", "error": str(e)}), 500
    finally:
        session.close()


@auth_blueprint.route('/login', methods=['POST'])
def login():
    session, _ = connect()

    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = authenticate_user(session, email, password)
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Welcome, {current_user}!"}), 200
