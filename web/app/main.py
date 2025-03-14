from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logging.info('Client disconnected')

@socketio.on('message')
def handle_message(message):
    logging.debug(f'Received message: {message}')
    emit('response', f'Server received: {message}')

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)
