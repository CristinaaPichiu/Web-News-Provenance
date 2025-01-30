from flask_mail import Mail, Message
from flask import current_app as app, request, jsonify
from itsdangerous import URLSafeTimedSerializer

mail = Mail()

def send_welcome_email(user_email, first_name):
    with app.app_context():
        msg = Message("Welcome to Our Platform!", sender=app.config['MAIL_USERNAME'], recipients=[user_email])
        msg.body = f"Hello {first_name},\n\nThank you for registering on our platform! We're excited to have you join our community."
        mail.send(msg)


def generate_reset_token(email):
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def send_reset_email(email, url):
    msg = Message("Reset Your Password", sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">Hello,</h2>
                    <p style="color: #555;">Please click on the button below to reset your password:</p>
                    <a href="{url}" style="text-decoration: none;">
                        <button style="
                            background-color: #6200ee;
                            color: white;
                            padding: 12px 24px;
                            border: none;
                            border-radius: 5px;
                            font-size: 16px;
                            cursor: pointer;
                            margin-top: 10px;
                            display: inline-block;">
                            Reset Password
                        </button>
                    </a>
                    <p style="color: #777; font-size: 14px; margin-top: 20px;">
                        If you did not request this, please ignore this email.
                    </p>
                    <p style="color: #777; font-size: 14px;">
                        Best Regards,<br>Your Team
                    </p>
                </div>
            </body>
        </html>
    """
    mail.send(msg)
