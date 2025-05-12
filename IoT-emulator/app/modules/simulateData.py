from main import _logger, opc_data_types, mqtt_host, opc_host, client_id
import asyncio, datetime, random, json
from asyncua import Client, ua
import paho.mqtt.client as mqtt

_discovered_opc_node_ids = {}

def send_mqtt(topic, message):
    if mqtt_client:
        _logger.debug(f'Sending MQTT | Topic: {topic} | Message: {message}')
        try:
            mqtt_client.publish(topic, message)
        except Exception as e:
            _logger.error(f"Error sending MQTT message: {e}")
    else:
        _logger.warning("MQTT client not connected. Cannot send message.")

async def send_opcua_values(iot_id, amps, volts, timestamp):
    if opc_client and _discovered_opc_node_ids:
        try:
            _logger.debug(f"Sending OPC | Iot ID: {iot_id}, Amps: {amps}, Volts: {volts}, Timestamp: {timestamp}")

            id_node = opc_client.get_node(_discovered_opc_node_ids["iot_id"])
            amps_node = opc_client.get_node(_discovered_opc_node_ids["amps"])
            volts_node = opc_client.get_node(_discovered_opc_node_ids["volts"])
            time_node = opc_client.get_node(_discovered_opc_node_ids["timestamp"])

            id_dv = ua.DataValue(ua.Variant(iot_id, opc_data_types["iot_id"]))
            amps_dv = ua.DataValue(ua.Variant(amps, opc_data_types["amps"]))
            volts_dv = ua.DataValue(ua.Variant(volts, opc_data_types["volts"]))
            time_dv = ua.DataValue(ua.Variant(timestamp, opc_data_types["timestamp"]))

            await id_node.write_value(id_dv)
            await amps_node.write_value(amps_dv)
            await volts_node.write_value(volts_dv)
            await time_node.write_value(time_dv)

            _logger.debug("Successfully wrote values to OPC UA.")

        except Exception as e:
            _logger.error(f"Error writing to OPC UA: {e}")
    else:
        _logger.warning("OPC UA client not connected or NodeIds not discovered. Cannot send values.")

async def discover_opc_nodes(client: Client):
    global _discovered_opc_node_ids
    _discovered_opc_node_ids = {} # Reset in case of reconnect

    try:
        _logger.info("Discovering OPC UA NodeIds...")
        uri = "opcua-server"
        ns_idx = await client.get_namespace_index(uri)
        _logger.debug(f"Discovered namespace index for '{uri}': {ns_idx}")

        if ns_idx is None:
             _logger.error(f"Namespace URI '{uri}' not found on server.")
             return False
        
        objects = client.get_objects_node()

        data_input_obj_node = await objects.get_child([f"{ns_idx}:DataInput"])
        _logger.debug(f"Found DataInput object: {data_input_obj_node}")

        input_id_node = await data_input_obj_node.get_child([f"{ns_idx}:input_iot_id"])
        input_amps_node = await data_input_obj_node.get_child([f"{ns_idx}:input_amps"])
        input_volts_node = await data_input_obj_node.get_child([f"{ns_idx}:input_volts"])
        input_time_node = await data_input_obj_node.get_child([f"{ns_idx}:input_timestamp"])

        _discovered_opc_node_ids = {
            "iot_id": input_id_node.nodeid,
            "amps": input_amps_node.nodeid,
            "volts": input_volts_node.nodeid,
            "timestamp": input_time_node.nodeid
        }

        _logger.info(f"Discovered OPC UA NodeIds: {_discovered_opc_node_ids}")
        return True

    except Exception as e:
        _logger.error(f"Error during OPC UA NodeId discovery: {e}")
        _discovered_opc_node_ids = {}
        return False

async def simulate_iot_data(iots, entities):
    global mqtt_client, opc_client

    # - - - Connect to MQTT - - -
    _logger.info(f"Connecting to MQTT broker at {mqtt_host}...")
    try:
        mqtt_client = mqtt.Client(client_id=client_id)
        mqtt_client.connect(mqtt_host, 1883, 60)
        mqtt_client.loop_start()
        _logger.info("MQTT client connected.")
    except Exception as e:
        _logger.error(f"Failed to connect to MQTT: {e}")
        mqtt_client = None

    # - - - Connect to OPC UA - - -
    opc_url = f"opc.tcp://admin@{opc_host}:4840"
    _logger.info(f"Connecting to OPC UA server at {opc_url}...")
    try:
        opc_client = Client(opc_url)
        await opc_client.connect()
        _logger.info("OPC UA client connected.")

        discovery_success = await discover_opc_nodes(opc_client)
        if not discovery_success:
            _logger.error("Failed to discover necessary OPC UA NodeIds. OPC UA functionality will be disabled.")
            await opc_client.disconnect()
            opc_client = None
    except Exception as e:
        _logger.error(f"Failed to connect to OPC UA: {e}")
        opc_client = None

    # - - - Data Sending Loop - - -
    if mqtt_client or opc_client:
        try:
            while True:
                entity = random.choice(entities)

                voltage_iot = None
                current_iot = None
                single_iot = False

                if entity.get('voltageIotId') == entity.get('currentIotId') and entity.get('voltageIotId') is not None:
                    single_iot = True
                    for iot in iots:
                        if iot.get('id') == entity['voltageIotId']:
                            iot_single = iot
                            break
                else:
                    for iot in iots:
                        if iot.get('id') == entity.get('voltageIotId'):
                            voltage_iot = iot
                        if iot.get('id') == entity.get('currentIotId'):
                            current_iot = iot
                        if voltage_iot and current_iot:
                            break

                if single_iot and not iot_single:
                     _logger.warning(f"Single IoT not found for entity {entity.get('id')}")
                     await asyncio.sleep(1)
                     continue
                elif not single_iot and (not voltage_iot or not current_iot):
                     _logger.warning(f"Voltage or Current IoT not found for entity {entity.get('id')}")
                     await asyncio.sleep(1)
                     continue

                voltage_rating = entity.get("voltageRating", 0.0)
                current_rating = entity.get("currentRating", 0.0)
                voltage_ten_percent = voltage_rating * 0.1

                sleep_duration = random.uniform(0.1, 1)
                current_time = datetime.datetime.now(datetime.timezone.utc)
                amps = random.uniform(0, current_rating)
                volts = random.uniform(voltage_rating - voltage_ten_percent, voltage_rating + voltage_ten_percent)

                if single_iot:
                    if iot_single.get('protocol') == 'mqtt':
                        send_mqtt(f"energy-data/{iot_single.get('id')}", json.dumps({
                            "timestamp": current_time.isoformat(),
                            "volts": round(volts, 2),
                            "amps": round(amps, 2),
                            "iotId": iot_single.get('id')
                        }))
                    elif iot_single.get('protocol') == 'opc':
                        await send_opcua_values(iot_single.get('id'), round(amps, 2), round(volts, 2), current_time)
                    else:
                         _logger.warning(f"Unknown protocol for single IoT: {iot_single.get('protocol')}")

                else:
                    # - - - Voltage - - -
                    if voltage_iot.get('protocol') == 'mqtt':
                        send_mqtt(f"{voltage_iot.get('id')}-energy-data", json.dumps({
                            "timestamp": current_time.isoformat(),
                            "volts": round(volts, 2),
                            "iotId": voltage_iot.get('id')
                        }))
                    elif voltage_iot.get('protocol') == 'opc':
                         await send_opcua_values(voltage_iot.get('id'), round(amps, 2), round(volts, 2), current_time)
                    else:
                         _logger.warning(f"Unknown protocol for voltage IoT: {voltage_iot.get('protocol')}")
                         
                    # - - - Current - - - 
                    if current_iot.get('protocol') == 'mqtt':
                        send_mqtt(f"{current_iot.get('id')}-energy-data", json.dumps({
                            "timestamp": current_time.isoformat(),
                            "amps": round(amps, 2),
                            "iotId": current_iot.get('id')
                        }))
                    elif current_iot.get('protocol') == 'opc':
                         await send_opcua_values(current_iot.get('id'), round(amps, 2), round(volts, 2), current_time)
                    else:
                         _logger.warning(f"Unknown protocol for current IoT: {current_iot.get('protocol')}")

                await asyncio.sleep(sleep_duration)

        except Exception as e:
            _logger.error(f"Error in simulation loop: {e}")
        finally:
            if mqtt_client:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
                _logger.info("MQTT client disconnected.")
            if opc_client:
                await opc_client.disconnect()
                _logger.info("OPC UA client disconnected.")
    else:
        _logger.error("Neither MQTT nor OPC UA client connected. Simulation loop will not start.")
