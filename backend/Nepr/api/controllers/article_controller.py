import logging

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from databases.db_postgresql_conn import connect
from api.services.sparql_service import SPARQLService
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

article_blueprint = Blueprint('article', __name__)
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
sparql_service = SPARQLService(service, options)


@article_blueprint.route('/create', methods=['POST'])
@jwt_required()
def create_article():
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    url = request.json.get('url')
    if not url:
        return jsonify({"message": "URL is required"}), 400

    success, message, graph_data = sparql_service.create_and_insert_graph(url)
    if success:
        return jsonify({
            "message": message,
            "data": graph_data,
            "format": "application/json"
        }), 201
    logging.info(graph_data)
    return jsonify({"message": "Failed", "error": message}), 500

@article_blueprint.route('/search', methods=['GET'])
@jwt_required()
def search_keywords():
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    keywords = request.args.get('keywords')
    if not keywords:
        return jsonify({"message": "Keywords are required"}), 400

    results, match_type = sparql_service.search_articles_by_keywords(keywords)
    if results:
        serializable_results = [
            {key: str(value) for key, value in article.items()}
            for article in results
        ]
        return jsonify({"message": "Success", "data": serializable_results, "type": match_type}), 200
    return jsonify({"message": "No articles found"}), 404

@article_blueprint.route("/search/advanced", methods=['GET'])
@jwt_required()
def search_advanced():
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    keywords = request.args.get('keywords')
    inLanguage = request.args.get('inLanguage')
    author_name = request.args.get('author')
    author_nationality = request.args.get('nationality')
    publisher = request.args.get('publisher')
    wordcount_min = request.args.get('wordcount_min')
    wordcount_max = request.args.get('wordcount_max')
    datePublished_min = request.args.get('datePublished_min')
    datePublished_max = request.args.get('datePublished_max')
    datePublished = None
    if not datePublished_max and not datePublished_min:
        datePublished = request.args.get('datePublished')
    wordcount = None
    if not wordcount_max and not wordcount_min:
        wordcount = request.args.get('wordcount')
    print(keywords, wordcount, inLanguage, author_name, author_nationality, publisher, datePublished, wordcount_min,
          wordcount_max, datePublished_min, datePublished_max)
    if not (
            keywords or wordcount_min or wordcount_max or datePublished_min or datePublished_max or wordcount or datePublished or inLanguage or author_name or author_nationality or publisher):
        return jsonify({"message": "A parameter is required"}), 400
    results, match_type = sparql_service.advanced_search(keywords, wordcount, inLanguage, author_name,
                                                         author_nationality, publisher, datePublished, wordcount_min,
                                                         wordcount_max, datePublished_min, datePublished_max)
    if results:
        serializable_results = [
            {key: str(value) for key, value in article.items()}
            for article in results
        ]
        return jsonify({"message": "Success", "data": serializable_results, "type": match_type}), 200
    return jsonify({"message": "No articles found"}), 404

@article_blueprint.route('/', methods=['GET'])
@jwt_required()
def get_article_by_url():
    """
    Retrieves an article from the Fuseki dataset by its URL.
    Args:
        url: URL of the article to retrieve.
    Returns:
        Article data in JSON-LD format.
    """
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    url = request.args.get('url')
    if not url:
        return jsonify({"message": "URL is required"}), 400
    result = sparql_service.get_article_by_url(url)
    if result:
        return jsonify({"message": "Success", "data": result}), 200

@article_blueprint.route('/all', methods=['GET'])
@jwt_required()
def get_all_articles():
    """
    Retrieves all articles from the Fuseki dataset.
    Returns:
        List of articles in JSON-LD format.
    """
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    results = sparql_service.get_all_articles()
    if results:
        return jsonify({"message": "Success", "data": results}), 200
    return jsonify({"message": "No articles found"}), 404

@article_blueprint.route('/', methods=['DELETE'])
@jwt_required()
def delete_article_by_url():
    """
    Deletes an article from the Fuseki dataset by its URL.
    Args:
        url: URL of the article to delete.
    Returns:
        Success message or error message.
    """
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    url = request.args.get('url')
    if not url:
        return jsonify({"message": "URL is required"}), 400
    success, message = sparql_service.delete_article_by_url(url)
    if success:
        return jsonify({"message": message}), 200
    return jsonify({"message": "Failed", "error": message}), 500

@article_blueprint.route('/data', methods=['GET'])
@jwt_required()
def get_all_data():
    """
    Retrieves all data from the Fuseki dataset.
    Returns:
        List of data in JSON-LD format.
    """
    try:
        verify_jwt_in_request()
    except Exception as e:
        logging.error(f"JWT verification failed: {str(e)}")
        return jsonify({"message": "Unauthorized"}), 401
    results = sparql_service.get_all_data()
    if results:
        return jsonify({"message": "Success", "data": results}), 200
    return jsonify({"message": "No data found"}), 404