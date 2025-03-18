import paho.mqtt.client as mqtt
import logging, time, os, datetime, random, json, requests

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

client_id = "fake_data_system"
client = mqtt.Client(client_id=client_id)

client.connect(mqtt_host, 1883, 60)

def send_mqtt(topic, message):
  logging.debug('Sending MQTT message')
  client.publish(topic, message)

devices = None
try:
  url = "http://devices:9002/devices/"

  response = requests.get(url)
  response.raise_for_status()
  devices = response.json()

  logging.info(f"Response Status Code: {response.status_code}")

except requests.exceptions.RequestException as e:
  logging.error(f"Error: {e}")
except json.JSONDecodeError:
  logging.error("Response is not valid JSON")
finally:
  if devices is None:
    logging.warning("No devices found")
    devices = [{"name":"Device 123","description":"A sensor device","id":"522d53dd-b6ba-4c57-9972-c8f2d491d138","dateCreated":"2025-03-18T12:18:03.884939Z"}]

num_devices = len(devices)
logging.info(f"Number of devices: {num_devices}")

while True:
  device = random.choice(devices)
  sleep = random.uniform(0.1,1)
  current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
  amps = random.randint(1,10)
  volts = random.randint(200,250)
  send_mqtt("energy-data", json.dumps({
    "timestamp": current_time,
    "amps": amps,
    "volts": volts,
    "deviceId": device["id"]
  }))
  time.sleep(sleep)

# client.disconnect()