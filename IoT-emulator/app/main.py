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

iots = None
iots_loaded = False

entities = None
entities_loaded = False

for attempt in range(attempts):
  if not iots_loaded:
    logging.info(f'Attempting to load IoTs | Attempt {attempt+1}/{attempts}')
    try:
      url = "http://device-management-system:9002/get/iot"

      response = requests.get(url)
      response.raise_for_status()
      iots = response.json()

      logging.info(f"Devices loaded")
      iots_loaded = True

    except requests.exceptions.RequestException as e:
      logging.error(f"Error: {e}")
      time.sleep(timeout)
    except json.JSONDecodeError:
      logging.error("Response is not valid JSON")
      time.sleep(timeout)
  else:
    break

for attempt in range(attempts):
  if not entities_loaded:
    logging.info(f'Attempting to load Entities | Attempt {attempt+1}/{attempts}')
    try:
      url = "http://device-management-system:9002/get/entity"

      response = requests.get(url)
      response.raise_for_status()
      entities = response.json()

      logging.info(f"Devices loaded")
      entities_loaded = True

    except requests.exceptions.RequestException as e:
      logging.error(f"Error: {e}")
      time.sleep(timeout)
    except json.JSONDecodeError:
      logging.error("Response is not valid JSON")
      time.sleep(timeout)
  else:
    break

if (iots is None or len(iots) == 0) & (entities is None or len(entities) == 0):
  logging.critical("No Iots or Entities were returned")
  mqtt_client.disconnect()
  opc_client.disconnect()
  sys.exit(1)

num_iots = len(iots)
logging.info(f"Number of iots: {num_iots}")
logging.info(f"Number of entities: {len(entities)}")

try:
  while True:
    entity = random.choice(entities)

    voltage_iot = None
    current_iot = None
    single_iot = False

    if entity['voltageIotId'] == entity['currentIotId']:
      single_iot = True
      for iot in iots:
        if iot['id'] == entity['voltageIotId']:
            iot_single = iot
    else:
      for iot in iots:
        if iot['id'] == entity['voltageIotId']:
            voltage_iot = iot
        if iot['id'] == entity['currentIotId']:
            current_iot = iot


    voltage_ten_percent=entity["voltageRating"]*0.1
    
    sleep = random.uniform(0.1,1)
    current_time = datetime.datetime.now(datetime.timezone.utc)
    amps = random.uniform(0,entity['currentRating'])
    volts = random.uniform(entity["voltageRating"]-voltage_ten_percent,entity["voltageRating"]+voltage_ten_percent)

    if single_iot:
      if iot_single['protocol'] == 'mqtt':
        send_mqtt(f"energy-data/{iot_single["id"]}", json.dumps({
          "timestamp": current_time.isoformat(),
          "volts": round(volts,2),
          "amps": round(amps,2),
          "iotId": iot_single["id"]
        }))
      elif iot_single['protocol'] == 'opc':
        send_opcua_values([iot_single["id"], round(amps,2), round(volts,2), current_time])
    else:
      # Voltage IoT
      if voltage_iot['protocol'] == 'mqtt':
        send_mqtt(f"{voltage_iot["id"]}-energy-data", json.dumps({
          "timestamp": current_time.isoformat(),
          "volts": round(volts,2),
          "iotId": voltage_iot["id"]
        }))
      elif voltage_iot['protocol'] == 'opc':
        send_opcua_values([voltage_iot["id"], round(amps,2), round(volts,2), current_time])
      
      # Current IoT
      if current_iot['protocol'] == 'mqtt':
        send_mqtt(f"{current_iot["id"]}-energy-data", json.dumps({
          "timestamp": current_time.isoformat(),
          "amps": round(amps,2),
          "iotId": current_iot["id"]
        }))
      elif current_iot['protocol'] == 'opc':
        send_opcua_values([current_iot["id"], round(amps,2), round(volts,2), current_time])
        
        
    time.sleep(sleep)
except Exception as e:
  logging.error(f"Error: {e}")
except KeyboardInterrupt:
  logging.info("Server stopped.")
finally:
  mqtt_client.disconnect()
  opc_client.disconnect()
  sys.exit()