import paho.mqtt.client as mqtt
import logging, time, os, datetime, random, json, requests

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")

client_id = "fake_data_system"
client = mqtt.Client(client_id=client_id)

client.connect(mqtt_host, 1883, 60)

def send_mqtt(topic, message):
  logging.debug(f'Sending MQTT message | Topic: {topic} | Message: {message}')
  client.publish(topic, message)

attempts = 3
timeout = 5
devices = None

for attempt in range(attempts):
  logging.info(f'Attempting to load devices | Attempt {attempt}/{attempts}')
  try:
    url = "http://devices:9002/devices/"

    response = requests.get(url)
    response.raise_for_status()
    devices = response.json()

    logging.info(f"Devices loaded")

  except requests.exceptions.RequestException as e:
    logging.error(f"Error: {e}")
    time.sleep(timeout)
  except json.JSONDecodeError:
    logging.error("Response is not valid JSON")
    time.sleep(timeout)


if devices is None or len(devices) == 0:
  logging.warning("No devices returned")
  devices = [{"name":"Fake Device","description":"Fake Sensor due to no devices being registered","id":"fake-id-here","dateCreated":"2025-03-18T12:18:03.884939Z"}]


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