from asyncua import Client, ua
from asyncua.common.subscription import Subscription
import asyncio, logging, json, requests

from models import Log, LogCreate

_logger = logging.getLogger(__name__)

_subscribed_iot_ids = set()

# - - - OPC UA Data Change Handler - - -
class OpcuaDataChangeHandler:
    def __init__(self, db_session_factory, sio_client, analysis_url):
        self._db_session_factory = db_session_factory
        self._sio_client = sio_client
        self._analysis_url = analysis_url
        self._iot_data_cache = {}
        self._lock = asyncio.Lock()

    async def datachange_notification(self, node, val, data):
        _logger.debug(f"OPC UA DataChange: Node {node.nodeid} changed to {val}")

        try:
            parent_node = await node.get_parent()
            browse_name = await parent_node.read_browse_name()

            try:
                iot_id_str = browse_name.name.replace("Iot_", "")
            except Exception as e:
                 _logger.error(f"OPC UA DataChange: Could not extract iot ID from browse name '{browse_name.name}': {e}")
                 return

            async with self._lock:
                if iot_id_str not in self._iot_data_cache:
                    self._iot_data_cache[iot_id_str] = {
                        "iotId": iot_id_str,
                        "volts": None,
                        "amps": None,
                        "timestamp": None
                    }

                node_display_name = await node.read_display_name()
                variable_name = node_display_name.text.lower()

                if variable_name in self._iot_data_cache[iot_id_str]:
                     self._iot_data_cache[iot_id_str][variable_name] = val
                else:
                     _logger.warning(f"OPC UA DataChange: Received update for unexpected variable '{variable_name}' on iot {iot_id_str}")
                     return

                cached_data = self._iot_data_cache[iot_id_str]
                if all(cached_data.get(key) is not None for key in ["volts", "amps", "timestamp"]):
                     _logger.info(f"OPC UA DataChange: Complete snapshot for iot {iot_id_str}")

                     log_create_data = {
                         "iotId": iot_id_str,
                         "volts": cached_data["volts"],
                         "amps": cached_data["amps"],
                         "timestamp": cached_data["timestamp"]
                     }
                     self._iot_data_cache[iot_id_str] = {
                        "iotId": iot_id_str,
                        "volts": None,
                        "amps": None,
                        "timestamp": None
                    }
                else:
                     _logger.debug(f"OPC UA DataChange: Partial snapshot for iot {iot_id_str}. Waiting for more data.")
                     return

            # - - - Process the complete snapshot - - -
            db = self._db_session_factory()
            log_entry = None

            try:
                payload_create = LogCreate(**log_create_data)
                log_entry = Log(**payload_create.dict())

                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                _logger.info(f"OPC UA Log entry added to database with ID: {log_entry.id}")

            except Exception as e:
                _logger.warning(f"OPC UA Error adding log entry to database: {e}")
                db.rollback()
            finally:
                db.close()

            if log_entry:
                try:
                    self._sio_client.emit('iot_data', {
                        'iotId': str(log_entry.iotId),
                        'source': {'protocol': 'opc'},
                        'volts': log_entry.volts,
                        'amps': log_entry.amps,
                        'timestamp': log_entry.timestamp.isoformat()
                    })
                    _logger.debug("OPC UA iot_data emitted successfully via SocketIO")
                except Exception as e:
                    _logger.error(f"OPC UA Error emitting iot_data via SocketIO: {e}")

                try:
                    url = self._analysis_url
                    headers = {"Content-Type": "application/json"}

                    analysis_data = {
                        "id": log_entry.id,
                        "iotId": str(log_entry.iotId),
                        "volts": log_entry.volts,
                        'amps': log_entry.amps,
                        "timestamp": log_entry.timestamp.isoformat()
                    }

                    response = requests.post(url, data=json.dumps(analysis_data), headers=headers)
                    response.raise_for_status()

                    _logger.info(f"OPC UA Data sent to analysis system. Response Status Code: {response.status_code}")

                except requests.exceptions.RequestException as e:
                    _logger.error(f"OPC UA Error sending data to analysis system: {e}")
                except Exception as e:
                    _logger.error(f"OPC UA An unexpected error occurred while sending to analysis system: {e}")

        except Exception as e:
            _logger.error(f"OPC UA Error in datachange_notification: {e}", exc_info=True)

# - - - OPC UA Client Setup Function - - -
async def setup_opcua_client(opc_url, opc_namespace_uri, opcua_handler, max_attempts=5, retry_delay=5):
    _logger.info(f"Attempting to connect to OPC UA server at {opc_url}...")
    opc_client = None
    opc_subscription = None

    for attempt in range(max_attempts):
        try:
            opc_client = Client(opc_url)
            await opc_client.connect()
            _logger.info("OPC UA client connected successfully.")

            opc_namespace_idx = await opc_client.get_namespace_index(opc_namespace_uri)
            _logger.info(f"OPC UA Namespace Index for '{opc_namespace_uri}': {opc_namespace_idx}")

            objects_node = opc_client.get_objects_node()

            iots_node_path_list = [f"{opc_namespace_idx}:Iots"]
            iots_node = await objects_node.get_child(iots_node_path_list)
            _logger.info(f"Found OPC UA 'Iots' node: {iots_node}")

            # - - - Setup OPC UA Subscription - - -
            opc_subscription = await opc_client.create_subscription(500, opcua_handler)
            _logger.info("OPC UA subscription created.")

            await discover_and_subscribe_iots(opc_client, opc_namespace_idx, iots_node, opc_subscription)

            return opc_client, opc_subscription

        except ConnectionRefusedError:
            _logger.warning(f"OPC UA connection refused. Attempt {attempt + 1}/{max_attempts}. Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
        except Exception as e:
            _logger.error(f"Failed to connect or setup OPC UA client (Attempt {attempt + 1}/{max_attempts}): {e}", exc_info=True)
            if opc_client:
                await opc_client.disconnect()
            await asyncio.sleep(retry_delay)

    _logger.critical(f"Failed to connect to OPC UA server after {max_attempts} attempts. Exiting.")
    return None, None

async def discover_and_subscribe_iots(opc_client, opc_namespace_idx, iots_node, opc_subscription):
    global _subscribed_iot_ids
    subscribed_nodes_count = 0

    try:
        iot_object_nodes = await iots_node.get_children()
        _logger.debug(f"Discovered {len(iot_object_nodes)} potential iot objects under 'Iots'.")

        for iot_obj_node in iot_object_nodes:
            try:
                browse_name = await iot_obj_node.read_browse_name()
                if browse_name.name.startswith("Iot_"):
                    iot_id = browse_name.name.replace("Iot_", "")

                    if iot_id not in _subscribed_iot_ids:
                        _logger.info(f"New iot discovered: {iot_id}. Attempting to subscribe...")

                        amps_var_node = await iot_obj_node.get_child([f"{opc_namespace_idx}:amps"])
                        volts_var_node = await iot_obj_node.get_child([f"{opc_namespace_idx}:volts"])
                        timestamp_var_node = await iot_obj_node.get_child([f"{opc_namespace_idx}:timestamp"])

                        await opc_subscription.subscribe_data_change(amps_var_node)
                        await opc_subscription.subscribe_data_change(volts_var_node)
                        await opc_subscription.subscribe_data_change(timestamp_var_node)

                        _logger.info(f"Subscribed to variables for new iot ID: {iot_id}")
                        _subscribed_iot_ids.add(iot_id)
                        subscribed_nodes_count += 3
                    else:
                         _logger.debug(f"Iot {iot_id} already subscribed. Skipping.")
                else:
                     _logger.debug(f"Skipping node with unexpected browse name format: {browse_name.name}")

            except Exception as e:
                _logger.error(f"Failed to subscribe to OPC UA nodes for discovered iot object {iot_obj_node}: {e}")

        _logger.debug(f"Discovery and subscription round finished. Subscribed to {len(_subscribed_iot_ids)} unique iots.")

    except Exception as e:
        _logger.error(f"Error during OPC UA iot discovery: {e}", exc_info=True)

async def periodic_discovery_task(opc_client, opc_namespace_uri, opc_subscription, interval=10):
    _logger.info(f"Starting periodic OPC UA iot discovery task (interval: {interval} seconds).")
    try:
        opc_namespace_idx = await opc_client.get_namespace_index(opc_namespace_uri)
        objects_node = opc_client.get_objects_node()
        iots_node_path_list = [f"{opc_namespace_idx}:Iots"]
        iots_node = await objects_node.get_child(iots_node_path_list)
        _logger.debug("Periodic discovery task initialized with namespace index and iots node.")
    except Exception as e:
        _logger.error(f"Failed to initialize periodic discovery task: {e}. Task will not run.")
        return

    while True:
        await asyncio.sleep(interval)
        _logger.debug("Running periodic OPC UA iot discovery...")
        try:
            await discover_and_subscribe_iots(opc_client, opc_namespace_idx, iots_node, opc_subscription)
        except Exception as e:
            _logger.error(f"Error during periodic OPC UA iot discovery task: {e}", exc_info=True)