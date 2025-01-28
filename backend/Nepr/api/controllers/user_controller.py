import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from api.services.sparql_service import SPARQLService
from api.services.user_service import UserService
from databases.db_postgresql_conn import connect
from flask_jwt_extended import get_jwt_identity
user_blueprint = Blueprint('user', __name__)

userService = UserService()
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
sparql_service = SPARQLService(service, options)

@user_blueprint.route('/history', methods=['POST'])
def add_user_history():
    """
    Adds an entry to the user's history.
    """
    email = request.json.get('email')
    url = request.json.get('url')
    logging.info(f"Adding user history for {email} and {url} and {datetime.now()}")
    session, _ = connect()
    result = userService.add_user_history(session, email, url)
    if result is None:
        return jsonify({"message": "Failed to add history"}), 500
    return jsonify({"message": "Success"}), 200

@user_blueprint.route('/recommend', methods=['GET'])
def recommend():
    """
    Recommends articles to the user based on their history.
    """
    email = request.args.get('email')
    logging.info(f"Getting recommendations for {email}")
    session, _ = connect()
    user_history = userService.get_user_history(session, email)
    if not user_history:
        return jsonify({"message": "No history found"}), 404
    recommended_articles = sparql_service.get_recommendations(user_history)
    if not recommended_articles:
        return jsonify({"message": "No recommendations found"}), 404
    return jsonify({"recommended_articles": recommended_articles}), 200