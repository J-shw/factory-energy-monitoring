import paho.mqtt.client as mqtt
import logging, time, os, datetime, random, json

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

client_id = "fake_data_system"
client = mqtt.Client(client_id=client_id)

client.connect(mqtt_host, 1883, 60)

def send_mqtt(topic, message):
  logging.debug('Sending MQTT message')
  client.publish(topic, message)
  

while True:
  sleep = random.uniform(0.1,1)
  current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
  amps = random.randint(1,10)
  volts = random.randint(200,250)
  send_mqtt("example-topic", json.dumps({
    "timestamp": current_time,
    "amps": amps,
    "volts": volts
  }))
  time.sleep(sleep)

# client.disconnect()