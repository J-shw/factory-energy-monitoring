import paho.mqtt.client as mqtt
import logging, os, socketio

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

sio = socketio.Client()
sio.connect('http://web:8080')

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    client.subscribe("example-topic")

def on_message(client, userdata, msg):
    logging.debug(f"Client '{client._client_id.decode('utf-8')}' received: {msg.topic} {msg.payload}")
    sio.emit('mqtt_message', {'topic': msg.topic, 'payload': msg.payload.decode('utf-8')})

client_id = "communication_system"
client = mqtt.Client(client_id=client_id)

client.on_connect = on_connect
client.on_message = on_message


client.connect(mqtt_host, 1883, 60)

client.loop_forever()