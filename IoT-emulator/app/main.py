import modules.simulateData as simulateData
from asyncua import ua
import asyncio, logging, time, os, json, requests, sys

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

mqtt_host = os.environ.get("MQTT_BROKER_HOST")
opc_host = os.environ.get("OPC_UA_SERVER_HOST")
client_id = "IoT_emulator"

opc_data_types = {
  "iot_id": ua.VariantType.String,
  "amps": ua.VariantType.Float,
  "volts": ua.VariantType.Float,
  "timestamp": ua.VariantType.DateTime
}

mqtt_client = None
opc_client = None
iots = None
entities = None

def load_data():
    global iots, entities
    attempts = 3
    timeout = 5

    iots_loaded = False
    entities_loaded = False

    for attempt in range(attempts):
        if not iots_loaded:
            _logger.info(f'Attempting to load IoTs | Attempt {attempt+1}/{attempts}')
            try:
                url = "http://device-management-system:9002/get/iot"
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                iots = response.json()
                _logger.info(f"IoTs loaded: {len(iots)}")
                iots_loaded = True
            except requests.exceptions.RequestException as e:
                _logger.error(f"Error loading IoTs: {e}")
                time.sleep(timeout)
            except json.JSONDecodeError:
                _logger.error("IoTs response is not valid JSON")
                time.sleep(timeout)
        else:
            break

    for attempt in range(attempts):
        if not entities_loaded:
            _logger.info(f'Attempting to load Entities | Attempt {attempt+1}/{attempts}')
            try:
                url = "http://device-management-system:9002/get/entity"
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                entities = response.json()
                _logger.info(f"Entities loaded: {len(entities)}")
                entities_loaded = True
            except requests.exceptions.RequestException as e:
                _logger.error(f"Error loading Entities: {e}")
                time.sleep(timeout)
            except json.JSONDecodeError:
                _logger.error("Entities response is not valid JSON")
                time.sleep(timeout)
        else:
            break

    if (iots is None or len(iots) == 0) and (entities is None or len(entities) == 0):
        _logger.critical("No IoTs or Entities were returned. Exiting.")
        sys.exit(1)

    _logger.info(f"Number of iots: {len(iots)}")
    _logger.info(f"Number of entities: {len(entities)}")


if __name__ == "__main__":
    load_data()
    try:
        asyncio.run(simulateData.simulate_iot_data(iots, entities))
    except KeyboardInterrupt:
        _logger.info("Simulation stopped by user.")
    except Exception as e:
        _logger.critical(f"An unhandled error occurred: {e}")