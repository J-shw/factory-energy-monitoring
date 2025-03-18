from flask import Flask, render_template, jsonify, request
from waitress import serve
import logging, requests

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/device')
def device_page():
    return render_template('device.html')

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


@app.route('/add/device', methods=['POST'])
def add_device():
    try:
        logging.info("Adding device")
        data = request.get_json()
        logging.debug(data)

        response = requests.post("http://devices:9002/device", json=data)

        if response.status_code == 201: 
            return jsonify(response.json()), 201
        else:
            return jsonify({"error": response.json()}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Device Management API: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == "__main__":
    logging.info("Starting web server with waitress")
    serve(app, host='0.0.0.0', port=8080)

