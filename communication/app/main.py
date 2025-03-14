import paho.mqtt.client as mqtt
import logging, os

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code "+str(rc))
    client.subscribe("example-topic")

def on_message(client, userdata, msg):
    logging.debug(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_host, 1883, 60)

client.loop_forever()