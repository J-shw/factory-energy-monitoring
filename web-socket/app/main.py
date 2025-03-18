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

@sio.event
def mqtt_data(sid, data):
    logging.debug(f'Received MQTT message from client {sid}: {data}')
    sio.emit('mqtt_message', {'topic': data['topic'], 'payload': data['payload'].decode('utf-8')})

if __name__ == '__main__':
    app = socketio.WSGIApp(sio)
    wsgi.server(eventlet.listen(('0.0.0.0', 8000)), app)
