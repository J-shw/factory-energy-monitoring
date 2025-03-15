import socketio, logging, eventlet
from eventlet import wsgi

logging.basicConfig(level=logging.INFO)

sio = socketio.Server(cors_allowed_origins='*')

@sio.event
def connect(sid, environ):
    logging.info(f'Client {sid} connected')

@sio.event
def disconnect(sid):
    logging.info(f'Client {sid} disconnected')

@sio.on('*')
def catch_all(event, sid, data):
    logging.debug(f'Received data on event {event} from client {sid}: {data}')

@sio.on('mqtt_data')
def handle_mqtt_message(sid, data):
    logging.debug(f'Received MQTT message: {data}')


if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    wsgi.server(eventlet.listen(('', 8000)), app)
