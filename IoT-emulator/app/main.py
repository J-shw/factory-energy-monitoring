import paho.mqtt.client as mqtt
from opcua import Client, ua
import logging, time, os, datetime, random, json, requests, sys

logging.basicConfig(level=logging.DEBUG)

mqtt_host = os.environ.get("MQTT_BROKER_HOST")
opc_host = os.environ.get("OPC_UA_SERVER_HOST")

client_id = "IoT_emulator"

mqtt_client = mqtt.Client(client_id=client_id)
mqtt_client.connect(mqtt_host, 1883, 60)

url = f"opc.tcp://{opc_host}:4840"
opc_client = Client(url)
opc_client.connect()
opc_node_ids = ["ns=2;i=2", "ns=2;i=3", "ns=2;i=4", "ns=2;i=5"] # Id, Amps, Volts, Timestamp
opc_data_types = [ua.VariantType.String, ua.VariantType.Float, ua.VariantType.Float, ua.VariantType.DateTime]

def send_mqtt(topic, message):
  logging.debug(f'Sending MQTT | Topic: {topic} | Message: {message}')
  mqtt_client.publish(topic, message)

def send_opcua_values(values):

    try:
        logging.debug(f"Sending OPC | Values: {values} | Nodes: {opc_node_ids}")

        for i, node_id in enumerate(opc_node_ids):
          node = opc_client.get_node(node_id)
   
          dv = ua.DataValue(ua.Variant(values[i], opc_data_types[i]))
          node.set_value(dv)

    except Exception as e:
        logging.error(f"Error writing to OPC UA: {e}")

attempts = 3
timeout = 5
devices = None
devices_loaded = False

for attempt in range(attempts):
  if not devices_loaded:
    logging.info(f'Attempting to load devices | Attempt {attempt+1}/{attempts}')
    try:
      url = "http://devices:9002/device-management-system/get/iot"

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
  logging.critical("No devices returned")
  mqtt_client.disconnect()
  opc_client.disconnect()
  sys.exit(1)

num_devices = len(devices)
logging.info(f"Number of devices: {num_devices}")

try:
  while True:

    device = random.choice(devices)

    voltage_ten_percent=device["voltage"]*0.1
    
    sleep = random.uniform(0.1,1)
    current_time = datetime.datetime.now(datetime.timezone.utc)
    amps = random.uniform(0,device['currentRatingAmps'])
    volts = random.uniform(device["voltage"]-voltage_ten_percent,device["voltage"]+voltage_ten_percent)

    if device['connectionType'] == 'mqtt':
      send_mqtt(f"{device["id"]}-energy-data", json.dumps({
        "timestamp": current_time.isoformat(),
        "amps": round(amps,2),
        "volts": round(volts,2),
        "deviceId": device["id"]
      }))
    elif device['connectionType'] == 'opc':
      send_opcua_values([device["id"], round(amps,2), round(volts,2), current_time])
      
    time.sleep(sleep)
except KeyboardInterrupt:
  logging.info("Server stopped.")
finally:
  mqtt_client.disconnect()