from modules.fastapi_app import create_app
from modules.mqtt_handler import setup_mqtt_client
from modules.opcua_handler import setup_opcua_client, OpcuaDataChangeHandler, periodic_discovery_task
import asyncio, logging, os, uvicorn

from models import SessionLocal

import socketio

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

# - - - Configuration - - -
mqtt_host = os.environ.get("MQTT_BROKER_HOST")
fastapi_host = os.environ.get("FASTAPI_HOST", "0.0.0.0")
fastapi_port = int(os.environ.get("FASTAPI_PORT", 9000))
opc_host = os.environ.get("OPC_UA_SERVER_HOST")
opc_port = int(os.environ.get("OPC_UA_SERVER_PORT", 4840))
opc_url = f"opc.tcp://{opc_host}:{opc_port}"
opc_namespace_uri = "opcua-server"
analysis_system_url = os.environ.get("ANALYSIS_SYSTEM_URL", "http://analysis-system:9090/process/")


sio = socketio.Client()

@sio.event
def connect():
    _logger.info("Connected to SocketIO server successfully")

@sio.event
def disconnect():
    _logger.info("Disconnected from SocketIO server")


_logger.debug("Attempting to connect to SocketIO server")
try:
    sio.connect('http://front-end:8080', transports=['websocket'], wait_timeout=5)
except Exception as e:
    _logger.error(f"Error connecting to SocketIO server: {e}")


async def main():
    # - - - Setup and Start MQTT Client - - -
    mqtt_client = setup_mqtt_client(
        mqtt_host=mqtt_host,
        client_id="communication_system",
        db_session_factory=SessionLocal,
        sio_client=sio,
        analysis_url=analysis_system_url
    )
    if mqtt_client:
         mqtt_client.loop_start()
         _logger.info("MQTT client loop started in background thread.")


    # - - - Setup and Connect OPC UA Client - - -
    opcua_handler = OpcuaDataChangeHandler(
        db_session_factory=SessionLocal,
        sio_client=sio,
        analysis_url=analysis_system_url
    )

    opc_client, opc_subscription = await setup_opcua_client(
        opc_url=opc_url,
        opc_namespace_uri=opc_namespace_uri,
        opcua_handler=opcua_handler
    )
    
    # --- Start Periodic OPC UA Discovery Task ---
    opc_discovery_task = None
    if opc_client and opc_subscription:
        _logger.info("Creating OPC UA periodic discovery task.")
        opc_discovery_task = asyncio.create_task(
            periodic_discovery_task(
                opc_client=opc_client,
                opc_namespace_uri=opc_namespace_uri,
                opc_subscription=opc_subscription,
                interval=15
            )
        )
        _logger.info("OPC UA periodic discovery task created.")
    else:
        _logger.warning("OPC UA client not connected, periodic discovery task will not start.")



    # - - - Setup and Run FastAPI Server - - -
    app = create_app()

    _logger.info(f"Starting FastAPI server on {fastapi_host}:{fastapi_port}...")
    config = uvicorn.Config(
        app,
        host=fastapi_host,
        port=fastapi_port,
        log_level="info"
    )
    server = uvicorn.Server(config)

    fastapi_task = asyncio.create_task(server.serve())
    _logger.info("FastAPI server task created.")


    # - - - Keep the event loop running - - -
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        _logger.info("Asyncio future cancelled.")

    # - - - Cleanup - - -
    _logger.info("Shutting down...")
    if mqtt_client:
        _logger.info("Stopping MQTT client loop...")
        mqtt_client.loop_stop()
        _logger.info("Disconnecting MQTT client...")
        mqtt_client.disconnect()
        _logger.info("MQTT client disconnected.")

    if opc_client:
        _logger.info("Disconnecting OPC UA client...")
        if opc_subscription:
            try:
                await opc_subscription.unsubscribe(opc_subscription.items)
                _logger.info("OPC UA unsubscribed from all items.")
            except Exception as e:
                _logger.error(f"Error during OPC UA unsubscribe: {e}")
        try:
            await opc_client.disconnect()
            _logger.info("OPC UA client disconnected.")
        except Exception as e:
            _logger.error(f"Error during OPC UA disconnect: {e}")
            
    if opc_discovery_task:
        _logger.info("Cancelling OPC UA periodic discovery task...")
        opc_discovery_task.cancel()
        try:
            await opc_discovery_task
        except asyncio.CancelledError:
            _logger.info("OPC UA periodic discovery task cancelled.")



# - - - Entry Point - - -
if __name__ == "__main__":
    _logger.info("Starting communication system...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("Communication system stopped by user (KeyboardInterrupt).")
    except Exception as e:
        _logger.critical(f"An unhandled error occurred during execution: {e}", exc_info=True)
    finally:
        _logger.info("Communication system finished.")