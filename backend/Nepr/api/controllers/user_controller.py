import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from api.services.sparql_service import SPARQLService
from api.services.user_service import UserService
from databases.db_postgresql_conn import connect
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, jwt_required
user_blueprint = Blueprint('user', __name__)

userService = UserService()
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
sparql_service = SPARQLService(service, options)

@user_blueprint.route('/history', methods=['POST'])
@jwt_required()
def add_user_history():
    """
    Adds an entry to the user's history.
    """
    try:
        verify_jwt_in_request()
        email = get_jwt_identity()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    url = request.json.get('url')
    logging.info(f"Adding user history for {email} and {url} and {datetime.now()}")
    session, _ = connect()
    result = userService.add_user_history(session, email, url)
    session.close()
    if result is None:
        return jsonify({"message": "Failed to add history"}), 500
    return jsonify({"message": "Success"}), 200

@user_blueprint.route('/recommend', methods=['GET'])
@jwt_required()
def recommend():
    """
    Recommends articles to the user based on their history.
    """
    try:
        verify_jwt_in_request()
        email = get_jwt_identity()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    logging.info(f"Getting recommendations for {email}")
    session, _ = connect()
    user_history = userService.get_user_history(session, email)
    session.close()
    if not user_history:
        return jsonify({"message": "No history found"}), 404
    recommended_articles = sparql_service.get_recommendations(user_history)
    if not recommended_articles:
        return jsonify({"message": "No recommendations found"}), 404
    return jsonify({"message":"Success","recommended_articles": recommended_articles}), 200

@jwt_required()
@user_blueprint.route('/history', methods=['GET'])
def get_user_history():
    """
    Gets the user's history.
    """
    try:
        verify_jwt_in_request()
        email = get_jwt_identity()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    logging.info(f"Getting history for {email}")
    session, engine = connect()
    user_history = userService.get_user_top_history(session, email, limit=10)
    session.close()
    if not user_history:
        return jsonify({"message": "No history found"}), 404
    logging.info(f"User history: {user_history}")
    links = [history for history in user_history]
    result = sparql_service.search_certain_articles(links)
    if result:
        return jsonify({"message": "Success", "data": result}), 200
    return jsonify({"message": "No articles found"}), 404