import paho.mqtt.client as mqtt
from opcua import Client
import logging, time, os, datetime, random, json, requests

logging.basicConfig(level=logging.DEBUG)
mqtt_host = os.environ.get("MQTT_BROKER_HOST")
opc_host = os.environ.get("OPC_UA_SERVER_HOST")

client_id = "fake_data_system"

mqtt_client = mqtt.Client(client_id=client_id)
mqtt_client.connect(mqtt_host, 1883, 60)

url = f"opc.tcp://{opc_host}:4840"
opc_client = Client(url)
opc_client.connect()
root = client.get_root_node()

def send_mqtt(topic, message):
  logging.debug(f'Sending MQTT message | Topic: {topic} | Message: {message}')
  mqtt_client.publish(topic, message)

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

try:
  while True:
    device = random.choice(devices)

    voltage_ten_percent=device["voltage"]*0.1
    
    sleep = random.uniform(0.1,1)
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    amps = random.uniform(0,device['currentRatingAmps'])
    volts = random.uniform(device["voltage"]-voltage_ten_percent,device["voltage"]+voltage_ten_percent)

    send_mqtt("energy-data", json.dumps({
      "timestamp": current_time,
      "amps": round(amps,2),
      "volts": round(volts,2),
      "deviceId": device["id"]
    }))
    time.sleep(sleep)
except KeyboardInterrupt:
  logging.info("Server stopped.")
finally:
  mqtt_client.disconnect()
