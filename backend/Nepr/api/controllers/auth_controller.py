import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from itsdangerous import URLSafeTimedSerializer
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from api.services.email_service import send_welcome_email
from databases.db_postgresql_conn import connect
from api.services.auth_service import get_user_by_email, create_user, authenticate_user
from models.models import User

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

    user = authenticate_user(session, email, password)
    if not user:
        return jsonify({"message": "Invalid email or password"}), 401

    # Setează 'sub' ca email și adaugă 'role' ca un claim custom
    additional_claims = {"role": user.role}
    access_token = create_access_token(identity=email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=email, additional_claims=additional_claims)

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



@auth_blueprint.route('/get-user-role', methods=['GET'])
@jwt_required()
def get_user_role():
    try:
        claims = get_jwt()
        role = claims['role']
        return jsonify({"role": role}), 200
    except KeyError:
        return jsonify({"error": "Role not found in JWT"}), 404
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@auth_blueprint.route('/get-users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        session, _ = connect()
        claims = get_jwt()

        # Verifică dacă utilizatorul este admin
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        # Selectează doar utilizatorii cu rolul "user"
        users = session.query(User).filter_by(role="user").all()

        users_list = [{
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role
        } for user in users]

        session.close()
        return jsonify(users_list), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

import uuid  # Importă biblioteca uuid pentru conversii

@auth_blueprint.route('/delete-user/<string:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Șterge un utilizator pe baza ID-ului (UUID).
    """
    try:
        session, _ = connect()
        claims = get_jwt()

        # Verifică dacă utilizatorul este admin
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        # Convertim user_id din string în UUID
        user_uuid = uuid.UUID(user_id)
        user = session.query(User).filter_by(id=user_uuid).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        session.delete(user)
        session.commit()
        return jsonify({"message": "User deleted successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400  # Dacă UUID-ul nu este valid
    except Exception as e:
        session.rollback()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        session.close()


@auth_blueprint.route('/update-user/<string:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        session, _ = connect()
        claims = get_jwt()

        # Verifică dacă utilizatorul este admin
        if claims.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        # Convertim user_id din string în UUID
        user_uuid = uuid.UUID(user_id)
        user = session.query(User).filter_by(id=user_uuid).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Verifică dacă request-ul conține body JSON
        if not request.json:
            return jsonify({"error": "Request body is empty"}), 400

        # Preluăm datele trimise de frontend
        data = request.get_json()

        if "password" in data and data["password"]:
            user.set_password(data["password"])  # Presupun că ai o metodă `set_password` care hash-uiește parola

        session.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except ValueError:
        return jsonify({"error": "Invalid user ID format"}), 400  # Dacă UUID-ul nu este valid
    except Exception as e:
        session.rollback()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        session.close()

@auth_blueprint.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    session, _ = connect()
    current_user_id = get_jwt_identity()  # Fetch the identity from JWT
    user_details = session.query(User).filter_by(email=current_user_id).first()

    if not user_details:
        return jsonify({"message": "User not found"}), 404

    # Extract passwords from the request
    current_password = request.json.get('currentPassword')
    new_password = request.json.get('newPassword')

    # Check the current password
    if not check_password_hash(user_details.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    # Update to the new password
    try:
        user_details.password_hash = generate_password_hash(new_password)
        session.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

