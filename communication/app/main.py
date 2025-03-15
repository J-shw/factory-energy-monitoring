import paho.mqtt.client as mqtt
import logging, os, socketio

logging.basicConfig(level=logging.DEBUG)

mqtt_host = os.environ.get("MQTT_BROKER_HOST")

sio = socketio.Client()

logging.debug("Attempting to connect to SocketIO server")
try:
    sio.connect('http://web-socket:8000', transports=['websocket'])
    logging.debug("Connected to SocketIO server successfully")
except Exception as e:
    logging.error(f"Error connecting to SocketIO server: {e}")

# MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("MQTT connected with result code "+str(rc))
    client.subscribe("example-topic")

def on_message(client, userdata, msg):
    logging.debug(f"Client '{client._client_id.decode('utf-8')}' received: {msg.topic} {msg.payload}")
    try:
        sio.emit('mqtt_message', {'topic': msg.topic, 'payload': msg.payload})
        logging.debug("mqtt_data emitted successfully")
    except Exception as e:
        logging.error(f"Error emitting mqtt_data: {e}")

client_id = "communication_system"
client = mqtt.Client(client_id=client_id)

client.on_connect = on_connect
client.on_message = on_message


client.connect(mqtt_host, 1883, 60)

client.loop_forever()