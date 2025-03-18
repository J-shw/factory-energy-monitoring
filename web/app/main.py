from flask import Flask, render_template, jsonify
from waitress import serve
import logging, requests

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/devices/<UID>')
def device(UID):
    try:
        data = requests.get(f'http://devices:9002/devices/{UID}')
        data.raise_for_status()
        return jsonify(data.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500 
    except ValueError:
        return jsonify({"error": "Invalid Json response"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    logging.info("Starting web server with waitress")
    serve(app, host='0.0.0.0', port=8080)

