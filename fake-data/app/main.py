import paho.mqtt.client as mqtt
import logging, time, os

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

def send_mqtt(host, port, topic, message):
  client = mqtt.Client()
  client.connect(host, port)
  client.publish(topic, message)
  client.disconnect()

while True:
  send_mqtt(mqtt_host, 1883, "example-topic", "Hello, MQTT!")
  time.sleep(1)