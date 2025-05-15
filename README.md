# factory-energy-monitoring
This is for my final year project at Bournemouth University (BU)

## Architecture

![FEM-MicroService-architecture drawio](https://github.com/user-attachments/assets/51f43e16-e225-4822-96af-b909977a1d3d)

## Front-End System
### Live data feeds
![live-view](https://github.com/user-attachments/assets/ac15d7b4-ec2c-463b-880d-ba2c72c1de5d)
- Real-time data updates using websockets
- Simple, modern graphs
### Events view
![events](https://github.com/user-attachments/assets/a3042c6d-878e-4233-9142-a57215d0c749)
- Quick and simple table view 
### Entity and IoT configuration
![iot-config](https://github.com/user-attachments/assets/d5c91f4a-4f0d-4636-a901-a9a790437f70)
![entity-config](https://github.com/user-attachments/assets/ad59c69d-0c37-4f23-a047-91f9d9e101f6)
- Easy configuration
## Device Management System
- Allows CRUD on device models
- View all created devices
- View specific device
- HTTP API

## IoT Emulation System
- Emulates IoT devices to showcase data flow and help development
- Uses created IoT's from Device Management System
- Sends random data as randomly selected IoTs with random intervals

## Commmunication System
- Central data acquisition system
- Relays different protocols to web socket for live data and HTTP for storage

## Analysis System
- Stores all device data
- HTTP API
- Analyises data *Not yet made*

## Database Server
- Postgress database
- Shell script for initialisation

## OPC-UA Server
- Hosts an OPC UA server 
- Allows dynamic OPC device assignment 
- Provides subscriptions to data flows


# Setup

## Docker

Quickly set up using the `docker-compose.yml` file.

* **Use existing images:**
    ```bash
    docker-compose up -d
    ```
* **Build images locally:** (Requires source files)
    ```bash
    docker-compose build
    docker-compose up -d
    ```