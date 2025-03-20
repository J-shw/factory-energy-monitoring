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
devices_loaded = False

for attempt in range(attempts):
  if not devices_loaded:
    logging.info(f'Attempting to load devices | Attempt {attempt+1}/{attempts}')
    try:
      url = "http://devices:9002/devices/"

      response = requests.get(url)
      response.raise_for_status()
      devices = response.json()

      logging.info(f"Devices loaded")
      devices_loaded = True

    except requests.exceptions.RequestException as e:
      logging.error(f"Error: {e}")
      time.sleep(timeout)
    except json.JSONDecodeError:
      logging.error("Response is not valid JSON")
      time.sleep(timeout)
  else:
    break

if devices is None or len(devices) == 0:
  logging.warning("No devices returned")
  devices = [{"name":"Fake Device","description":"Fake Sensor due to no devices being registered","id":"fake-id-here","dateCreated":"2025-03-18T12:18:03.884939Z"}]


num_devices = len(devices)
logging.info(f"Number of devices: {num_devices}")

while True:
  device = random.choice(devices)
  
  voltage_ten_percent=device["voltage"]*0.1
  
  sleep = random.uniform(0.1,1)
  current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
  amps = random.randint(0,device['currentRatingAmps'])
  volts = random.randint(device["voltage"]-voltage_ten_percent,device["voltage"]+voltage_ten_percent)

  send_mqtt("energy-data", json.dumps({
    "timestamp": current_time,
    "amps": amps,
    "volts": volts,
    "deviceId": device["id"]
  }))
  time.sleep(sleep)

# client.disconnect()