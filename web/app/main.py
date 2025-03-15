from flask import Flask, render_template, jsonify
from waitress import serve
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    logging.info("Starting web server with waitress")
    serve(app, host='0.0.0.0', port=8080)

