from flask_mail import Mail, Message
from flask import current_app as app

mail = Mail()

def send_welcome_email(user_email, first_name):
    with app.app_context():
        msg = Message("Welcome to Our Platform!", sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        msg.body = f"Hello {first_name},\n\nThank you for registering on our platform! We're excited to have you join our community."
        mail.send(msg)
