import paho.mqtt.client as mqtt
import logging, time, os

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

client_id = "fake_data_system"
client = mqtt.Client(client_id=client_id)

client.connect(mqtt_host, 1883, 60)

def send_mqtt(topic, message):
  logging.debug('Sending MQTT message')
  client.publish(topic, message)
  

while True:
  send_mqtt("example-topic", "Hello, MQTT!")
  time.sleep(1)

# client.disconnect()