import logging
import coloredlogs
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log')
coloredlogs.install(level='INFO', fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)
SERVICES = {
    "user": "http://127.0.0.1:5002",
    "article": "http://127.0.0.1:5001",
    "auth": "http://127.0.0.1:5002",
    "email": "http://127.0.0.1:5002"
}

TIMEOUT = 60


@app.route('/<service>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
@app.route('/<service>/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(service, path=""):
    if service not in SERVICES:
        return jsonify({"error": f"Service '{service}' not found"}), 404
    logging.info(f"Proxying request to {service} service {path}")
    service_url = SERVICES[service]
    if path:
        full_url = f"{service_url}/{service}/{path}"
    else:
        full_url = f"{service_url}/{service}"
    if request.args:
        full_url += '?' + request.query_string.decode('utf-8')

    print("full_url: " + full_url)  # Log the full URL for debugging

    try:
        if request.method == 'OPTIONS':
            return jsonify({"message": "Preflight request successful"}), 200

        response = requests.request(
            method=request.method,
            url=full_url,
            headers={key: value for key, value in request.headers if key != "Host"},
            params=request.args,  # Forward the query parameters
            json=request.get_json(silent=True),  # Forward the JSON body if present
            timeout=TIMEOUT
        )

        if response.content:
            return jsonify(response.json()), response.status_code
        else:
            return jsonify({"error": f"{service} service error", "details": "Empty response"}), 500

    except requests.exceptions.ConnectionError:
        return jsonify({"error": f"{service} service is unavailable", "details": "Connection refused"}), 503

    except requests.exceptions.Timeout:
        return jsonify({"error": f"{service} service timeout", "details": "The request took too long"}), 504

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"{service} service error", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
