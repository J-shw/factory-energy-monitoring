from asyncua import Server, ua
from asyncua.ua import NodeId
from datetime import datetime, timezone
import asyncio, logging

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger('asyncua')

iot_nodes = {}

class SubHandler:
    def __init__(self, server_instance):
        self.server = server_instance

    async def datachange_notification(self, node, val, data):
        _logger.debug(f"Data change on node {node.nodeid}: {val}")

        try:
            server = self.server
            input_obj_node = await node.get_parent()

            try:
                 ns_idx = await server.get_namespace_index("opcua-server")
                 if ns_idx is None:
                      _logger.error("Namespace URI 'opcua-server' not found on server.")
                      return
            except Exception as e:
                 _logger.error(f"Could not get namespace index in handler: {e}")
                 return

            try:
                input_iot_id_node = await input_obj_node.get_child([f"{ns_idx}:input_iot_id"])
                input_amps_node = await input_obj_node.get_child([f"{ns_idx}:input_amps"])
                input_volts_node = await input_obj_node.get_child([f"{ns_idx}:input_volts"])
                input_timestamp_node = await input_obj_node.get_child([f"{ns_idx}:input_timestamp"])
            except Exception as e:
                _logger.error(f"Error finding input nodes under DataInput: {e}")
                return

            iot_id_dv = await input_iot_id_node.read_data_value() if input_iot_id_node else None
            amps_dv = await input_amps_node.read_data_value() if input_amps_node else None
            volts_dv = await input_volts_node.read_data_value() if input_volts_node else None
            timestamp_dv = await input_timestamp_node.read_data_value() if input_timestamp_node else None

            iot_id = iot_id_dv.Value.Value if iot_id_dv and iot_id_dv.Value and iot_id_dv.Value.Value is not None else None
            amps = amps_dv.Value.Value if amps_dv and amps_dv.Value and amps_dv.Value.Value is not None else None
            volts = volts_dv.Value.Value if volts_dv and volts_dv.Value and volts_dv.Value.Value is not None else None
            timestamp = timestamp_dv.Value.Value if timestamp_dv and timestamp_dv.Value and timestamp_dv.Value.Value is not None else None

            _logger.info(f"Received data for Iot ID: {iot_id}, Amps: {amps}, Volts: {volts}, Timestamp: {timestamp}")

            global iot_nodes

            server = self.server
            objects = server.get_objects_node()

            try:
                iots_obj_node = await objects.get_child([f"{ns_idx}:Iots"])
            except Exception as e:
                _logger.error(f"Error finding Iots object: {e}")
                return


            if iot_id and iot_id not in iot_nodes:
                _logger.info(f"Creating new node for iot: {iot_id}")

                iot_obj_node = await iots_obj_node.add_object(NodeId(f"Iot_{iot_id}", ns_idx, ua.NodeIdType.String), f"Iot_{iot_id}")

                _logger.info(f"DEBUG: After add_object - iot_obj_node NodeId: {iot_obj_node.nodeid if iot_obj_node else 'None'} (Type: {type(iot_obj_node)})")

                iot_id_var = await iot_obj_node.add_variable(ns_idx, "iot_id", iot_id, varianttype=ua.VariantType.String)
                await iot_id_var.set_writable()

                _logger.debug(f"Created variable iot_id NodeId: {iot_id_var.nodeid}")

                amps_var = await iot_obj_node.add_variable(ns_idx, "amps", amps, varianttype=ua.VariantType.Float)
                await amps_var.set_writable()
                _logger.debug(f"Created variable amps NodeId: {amps_var.nodeid}")

                volts_var = await iot_obj_node.add_variable(ns_idx, "volts", volts, varianttype=ua.VariantType.Float)
                await volts_var.set_writable()
                _logger.debug(f"Created variable volts NodeId: {volts_var.nodeid}")

                timestamp_var = await iot_obj_node.add_variable(ns_idx, "timestamp", timestamp, varianttype=ua.VariantType.DateTime)
                await timestamp_var.set_writable()
                _logger.debug(f"Created variable timestamp NodeId: {timestamp_var.nodeid}")

                iot_nodes[iot_id] = {
                    "obj": iot_obj_node,
                    "amps": amps_var,
                    "volts": volts_var,
                    "timestamp": timestamp_var
                }
            elif iot_id in iot_nodes:
                _logger.info(f"Updating existing node for iot: {iot_id}")
                iot_info = iot_nodes[iot_id]

                if amps is not None:
                    await iot_info["amps"].write_value(ua.DataValue(ua.Variant(amps, ua.VariantType.Float)))
                if volts is not None:
                    await iot_info["volts"].write_value(ua.DataValue(ua.Variant(volts, ua.VariantType.Float)))
                if timestamp is not None:
                    await iot_info["timestamp"].write_value(ua.DataValue(ua.Variant(timestamp, ua.VariantType.DateTime)))

            elif iot_id is None:
                 _logger.warning("Received data change with invalid/None iot_id. Skipping node creation/update.")


        except Exception as e:
            _logger.error(f"Error in data change callback: {e}", exc_info=True) # Log traceback

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840")

    uri = "opcua-server"
    idx = await server.register_namespace(uri)

    _logger.info(f"Server namespace index for '{uri}': {idx}")

    objects = server.get_objects_node()

    iots_obj = await objects.add_object(idx, "Iots")
    data_input_obj = await objects.add_object(idx, "DataInput")

    input_id_var = await data_input_obj.add_variable(idx, "input_iot_id", "", varianttype=ua.VariantType.String)
    await input_id_var.set_writable()
    _logger.info(f"input_iot_id NodeId: {input_id_var.nodeid}")

    input_amps_var = await data_input_obj.add_variable(idx, "input_amps", 0.0, varianttype=ua.VariantType.Float)
    await input_amps_var.set_writable()
    _logger.info(f"input_amps_var NodeId: {input_amps_var.nodeid}")

    input_volts_var = await data_input_obj.add_variable(idx, "input_volts", 0.0, varianttype=ua.VariantType.Float)
    await input_volts_var.set_writable()
    _logger.info(f"input_volts_var NodeId: {input_volts_var.nodeid}") 

    input_time_var = await data_input_obj.add_variable(idx, "input_timestamp", datetime.now(timezone.utc), varianttype=ua.VariantType.DateTime)
    await input_time_var.set_writable()
    _logger.info(f"input_timestamp_var NodeId: {input_time_var.nodeid}")

    handler_instance = SubHandler(server)
    sub = await server.create_subscription(1000, handler_instance)

    await sub.subscribe_data_change(input_id_var)
    await sub.subscribe_data_change(input_amps_var)
    await sub.subscribe_data_change(input_volts_var)
    await sub.subscribe_data_change(input_time_var)

    _logger.info('Starting server!')
    await server.start()

    _logger.info(f"OPC UA server started on {server.endpoint}.")

    try:
        await asyncio.Future() # Keep the server running
    finally:
        _logger.info('Stopping server!')
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())