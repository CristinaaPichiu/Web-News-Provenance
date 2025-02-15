from flask import Flask

from api.controllers.article_controller import article_blueprint
from api.controllers.auth_controller import auth_blueprint
from api.controllers.email_controller import email_blueprint
from api.controllers.user_controller import user_blueprint


def register_routes_article(app: Flask):
    """
    Record all application blueprints.
    """
    app.register_blueprint(article_blueprint, url_prefix='/article')

def register_routes_auth(app: Flask):
    """
    Record all application blueprints.
    """
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(email_blueprint, url_prefix='/email')

