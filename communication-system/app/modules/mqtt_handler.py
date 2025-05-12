import paho.mqtt.client as mqtt
from models import Log, LogCreate 
import logging, json, requests

_logger = logging.getLogger(__name__)

# - - - MQTT Callbacks - - -
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        _logger.info("MQTT connected successfully")
        client.subscribe("energy-data/+")
        _logger.info("Subscribed to topic: energy-data/+")
    else:
        _logger.error(f"MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    _logger.debug(f"MQTT Client '{client._client_id.decode('utf-8')}' received: {msg.topic} {msg.payload}")
    msgPayload = msg.payload.decode('utf-8')

    db_session_factory = userdata["db_session_factory"]
    sio_client = userdata["sio_client"]
    analysis_url = userdata["analysis_url"]

    db = db_session_factory()
    log_entry = None

    try: # Store data
        payload_create = LogCreate(**json.loads(msgPayload))
        log_entry = Log(**payload_create.dict())

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        _logger.info(f"MQTT Log entry added to database with ID: {log_entry.id}")

    except json.JSONDecodeError:
        _logger.error(f"MQTT Received invalid JSON payload: {msgPayload}")
        db.rollback()
    except Exception as e:
        _logger.warning(f"MQTT Error adding log entry to database: {e}")
        db.rollback()
    finally:
        db.close()

    if log_entry:
        try: # Emit data to SocketIO
            sio_client.emit('iot_data', {
                'iotId': str(log_entry.iotId),
                'source': {'protocol': 'mqtt' ,'topic': msg.topic},
                'volts': log_entry.volts,
                'amps': log_entry.amps,
                'timestamp': log_entry.timestamp.isoformat()
            })
            _logger.debug("MQTT iot_data emitted successfully via SocketIO")
        except Exception as e:
            _logger.error(f"MQTT Error emitting iot_data via SocketIO: {e}")

        try: # Stream data for analysis via HTTP POST
            url = analysis_url
            headers = {"Content-Type": "application/json"}

            analysis_data = {
                "id": log_entry.id,
                "iotId": str(log_entry.iotId),
                "volts": log_entry.volts,
                "amps": log_entry.amps,
                "timestamp": log_entry.timestamp.isoformat()
            }
            
            response = requests.post(url, data=json.dumps(analysis_data), headers=headers)
            response.raise_for_status()

            _logger.info(f"MQTT Data sent to analysis system. Response Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            _logger.error(f"MQTT Error sending data to analysis system: {e}")
        except Exception as e:
            _logger.error(f"MQTT An unexpected error occurred while sending to analysis system: {e}")


# - - - MQTT Client Setup Function - - -
def setup_mqtt_client(mqtt_host, client_id, db_session_factory, sio_client, analysis_url):
    _logger.info(f"Setting up MQTT client with ID: {client_id}")
    client = mqtt.Client(client_id=client_id)

    client.user_data_set({
        "db_session_factory": db_session_factory,
        "sio_client": sio_client,
        "analysis_url": analysis_url
    })

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(mqtt_host, 1883, 60)
        _logger.info("MQTT client connect call successful.")
        return client
    except Exception as e:
        _logger.error(f"Failed to connect MQTT client: {e}")
        return None