import asyncio
import logging
from asyncua import Server, ua
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

iot_nodes = {}

async def data_change_callback(node, val, data):
    _logger.info(f"Data change on node {node.nodeid}: {val}")

    input_obj_node = node.get_parent()

    input_iot_id_node = input_obj_node.get_child(["2:input_iot_id"])
    input_amps_node = input_obj_node.get_child(["2:input_amps"])
    input_volts_node = input_obj_node.get_child(["2:input_volts"])
    input_timestamp_node = input_obj_node.get_child(["2:input_timestamp"])

    try:
        iot_id = await input_iot_id_node.read_value()
        amps = await input_amps_node.read_value()
        volts = await input_volts_node.read_value()
        timestamp = await input_timestamp_node.read_value()

        _logger.info(f"Received data for Iot ID: {iot_id}, Amps: {amps}, Volts: {volts}, Timestamp: {timestamp}")

        server = node.get_server()
        objects = server.get_objects_node()
        iots_obj_node = await objects.get_child(["2:Iots"])

        if iot_id not in iot_nodes:
            _logger.info(f"Creating new node for iot: {iot_id}")

            iot_obj_node = await iots_obj_node.add_object(server.get_namespace_index("opcua-server"), f"Iot_{iot_id}")

            iot_id_var = await iot_obj_node.add_variable(server.get_namespace_index("opcua-server"), "iot_id", iot_id, varianttype=ua.VariantType.String)
            await iot_id_var.set_writable()
            amps_var = await iot_obj_node.add_variable(server.get_namespace_index("opcua-server"), "amps", amps, varianttype=ua.VariantType.Float)
            await amps_var.set_writable()
            volts_var = await iot_obj_node.add_variable(server.get_namespace_index("opcua-server"), "volts", volts, varianttype=ua.VariantType.Float)
            await volts_var.set_writable()
            timestamp_var = await iot_obj_node.add_variable(server.get_namespace_index("opcua-server"), "timestamp", timestamp, varianttype=ua.VariantType.DateTime)
            await timestamp_var.set_writable()

            iot_nodes[iot_id] = {
                "obj": iot_obj_node,
                "amps": amps_var,
                "volts": volts_var,
                "timestamp": timestamp_var
            }
        else:
            _logger.info(f"Updating existing node for iot: {iot_id}")
            iot_info = iot_nodes[iot_id]
            await iot_info["amps"].write_value(amps)
            await iot_info["volts"].write_value(volts)
            await iot_info["timestamp"].write_value(timestamp)

    except Exception as e:
        _logger.error(f"Error in data change callback: {e}")


async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840")

    uri = "opcua-server"
    idx = await server.register_namespace(uri)

    objects = server.get_objects_node()

    iots_obj = await objects.add_object(idx, "Iots")

    data_input_obj = await objects.add_object(idx, "DataInput")

    input_id_var = await data_input_obj.add_variable(idx, "input_iot_id", "", varianttype=ua.VariantType.String)
    await input_id_var.set_writable()

    input_amps_var = await data_input_obj.add_variable(idx, "input_amps", 0.0, varianttype=ua.VariantType.Float)
    await input_amps_var.set_writable()

    input_volts_var = await data_input_obj.add_variable(idx, "input_volts", 0.0, varianttype=ua.VariantType.Float)
    await input_volts_var.set_writable()

    input_time_var = await data_input_obj.add_variable(idx, "input_timestamp", datetime.now(timezone.utc), varianttype=ua.VariantType.DateTime)
    await input_time_var.set_writable()

    handler = data_change_callback
    sub = await server.create_subscription(1000, handler)

    await sub.subscribe_data_change(input_id_var)
    await sub.subscribe_data_change(input_amps_var)
    await sub.subscribe_data_change(input_volts_var)
    await sub.subscribe_data_change(input_time_var)


    _logger.info('Starting server!')
    await server.start()

    _logger.info("OPC UA server started. Press Ctrl+C to stop.")

    try:
        await asyncio.Future()
    finally:
        _logger.info('Stopping server!')
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
