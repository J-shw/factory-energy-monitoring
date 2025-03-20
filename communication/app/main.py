import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from models import Log, SessionLocal, LogCreate, LogOut
import logging, os, socketio, json, requests

logging.basicConfig(level=logging.DEBUG)

mqtt_host = os.environ.get("MQTT_BROKER_HOST")

sio = socketio.Client()

logging.debug("Attempting to connect to SocketIO server")
try:
    sio.connect('http://web-socket:8000', transports=['websocket'])
    logging.debug("Connected to SocketIO server successfully")
except Exception as e:
    logging.error(f"Error connecting to SocketIO server: {e}")

# MQTT
def on_connect(client, userdata, flags, rc):
    logging.info("MQTT connected with result code "+str(rc))
    client.subscribe("energy-data")

def on_message(client, userdata, msg):
    logging.debug(f"Client '{client._client_id.decode('utf-8')}' received: {msg.topic} {msg.payload}")
    try:
        sio.emit('mqtt_data', {'topic': msg.topic, 'payload': msg.payload})
        logging.debug("mqtt_data emitted successfully")
    except Exception as e:
        logging.error(f"Error emitting mqtt_data: {e}")
    try:
        url = "http://analysis:9090/events/"
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data=msg.payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        logging.info(f"Response Status Code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Error: {e}")
    except json.JSONDecodeError:
        logging.error("Response is not valid JSON")
    try:
        db = SessionLocal()
        payload_str = msg.payload.decode('utf-8')
        payload_dict = json.loads(payload_str)

        log_entry = Log(**payload_dict) #unpack the dictionary into the Log constructor.

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        db.close()
        logging.info("Log entry added to database")

    except Exception as e:
        logging.warning(f"Error adding log entry: {e}")
        db.rollback()
    finally:
        db.close()


client_id = "communication_system"
client = mqtt.Client(client_id=client_id)

client.on_connect = on_connect
client.on_message = on_message


client.connect(mqtt_host, 1883, 60)

client.loop_forever()