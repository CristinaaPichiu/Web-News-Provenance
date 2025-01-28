from werkzeug.security import generate_password_hash
from models.models import User
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash


def get_user_by_email(session: Session, email: str):
    """
    Returns the user with the specified email.
    """
    return session.query(User).filter_by(email=email).first()

def create_user(session: Session, email: str, password: str, first_name: str = '', last_name: str = '', role='user'):
    """
    Create a new user in the database.
    """
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(email=email, first_name=first_name, last_name=last_name, password_hash=hashed_password, role=role)
    session.add(new_user)
    return new_user

def authenticate_user(session, email, password):
    """
    Validates the user based on email and password.
    Returns the user if authentication is successful, otherwise None.
    """
    user = session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        return user
    return None