from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import logging, requests, eventlet

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index_page():
    return render_template('live.html')

@app.route('/configuration')
def configuration_page():
    return render_template('configuration.html')

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

# Proxies - - - -

@app.route('/get/iot', methods=['GET'])
def get_iot():
    try:
        data = requests.get('http://device-management-system:9002/get/iot')
        data.raise_for_status()
        return jsonify(data.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500 
    except ValueError:
        return jsonify({"error": "Invalid Json response"}), 500

@app.route('/get/iot/<uid>', methods=['GET'])
def get_iot_by_uid(uid):
    try:
        data = requests.get(f'http://device-management-system:9002/get/iot/{uid}')
        data.raise_for_status()
        return jsonify(data.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500 
    except ValueError:
        return jsonify({"error": "Invalid Json response"}), 500

@app.route('/get/entity/', methods=['GET'])
def get_entity():
    try:
        data = requests.get(f'http://device-management-system:9002/get/entity/')
        data.raise_for_status()
        return jsonify(data.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500 
    except ValueError:
        return jsonify({"error": "Invalid Json response"}), 500

@app.route('/get/entity/<UID>', methods=['GET'])
def get_entity_by_uid(UID):
    try:
        data = requests.get(f'http://device-management-system:9002/get/entity/{UID}')
        data.raise_for_status()
        return jsonify(data.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500 
    except ValueError:
        return jsonify({"error": "Invalid Json response"}), 500

@app.route('/get/event/', methods=['GET'])
def get_event():
    try:
        data = requests.get(f'http://analysis-system:9090/get/event/')
        data.raise_for_status()
        return jsonify(data.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500 
    except ValueError:
        return jsonify({"error": "Invalid Json response"}), 500
    
@app.route('/create/iot', methods=['POST'])
def add_device():
    try:
        logging.info("Adding device")
        data = request.get_json()
        logging.debug(data)

        response = requests.post("http://device-management-system:9002/create/iot", json=data)

        if response.status_code == 201: 
            return jsonify(response.json()), 201
        else:
            return jsonify({"error": response.json()}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error communicating with Device Management System API: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# Websocket - - - -

@socketio.on('connect')
def connect():
    logging.info(f'Client connected')

@socketio.on('disconnect')
def disconnect():
    logging.info(f'Client disconnected')

@socketio.on('iot_data')
def handle_iot_data(data):
    logging.debug(f'Received IoT message: {data}')
    emit('iot_message', data, broadcast=True)

if __name__ == "__main__":
    logging.info("Starting web systems")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8080)), app)