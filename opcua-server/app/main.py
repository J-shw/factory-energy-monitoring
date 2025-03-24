from opcua import Server, ua
import logging

logging.basicConfig(level=logging.INFO)


server = Server()
server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

objects = server.get_objects_node()
myobj = objects.add_object("ns=2;i=1", "MyObject")
myvar = myobj.add_variable("ns=2;i=2", "MyVariable", 0)
myvar.set_writable()

server.start()

logging.info("OPC UA server started. Press Ctrl+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    logging.info("Server stopped.")
finally:
    server.stop()