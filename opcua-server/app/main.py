from opcua import Server, ua
import logging

logging.basicConfig(level=logging.INFO)


server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

objects = server.get_objects_node()

energyDataObj = objects.add_object("ns=2;i=1", "energyData")

idVar = energyDataObj.add_variable("ns=2;i=2", "device_id", ua.VariantType.String)
idVar.set_writable()
ampsVar = energyDataObj.add_variable("ns=2;i=3", "amps", ua.VariantType.Float)
ampsVar.set_writable()
voltsVar = energyDataObj.add_variable("ns=2;i=4", "volts", ua.VariantType.Float)
voltsVar.set_writable()
timeVar = energyDataObj.add_variable("ns=2;i=5", "timestamp", ua.VariantType.DateTime)
timeVar.set_writable()

server.start()

logging.info("OPC UA server started. Press Ctrl+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    logging.info("Server stopped.")
finally:
    server.stop()