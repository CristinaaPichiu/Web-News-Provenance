from flask import Flask

from api.controllers.article_controller import article_blueprint
from api.controllers.auth_controller import auth_blueprint

def register_routes(app: Flask):
    """
    Record all application blueprints.
    """
    app.register_blueprint(article_blueprint, url_prefix='/article')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
