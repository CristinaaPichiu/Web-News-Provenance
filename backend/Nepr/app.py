import logging
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from api.routes.routes import register_routes
from datetime import timedelta
import coloredlogs

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='app.log')
coloredlogs.install(level='INFO', fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Preia cheia din mediul de lucru
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

register_routes(app)


if __name__ == '__main__':
    app.run()
