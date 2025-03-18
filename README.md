# factory-energy-monitoring
This is for my final year project at Bournemouth University (BU)


## Web
![Screenshot 2025-03-18 at 15-55-39 FEMS - Home](https://github.com/user-attachments/assets/1d4b68d2-6d96-4a5b-84ab-9cf7ae877abb)

- Dynamically generated graph
- Real-time data updates using websockets
- Simple, modern graphs

## Device system
- Allows CRUD on device models
- View all created devices
- View specific device
- HTTP API

## Fake data system
- Simulates MQTT device messages
- Uses created devices from device system
- Sends random data to randomly selected devices at random intervals

## Commmunication system
- Central data acquisition system
- Relays different protocls to web socket for live data and HTTP for storage

## Analysis system
- Stores all device data
- HTTP API
- Analyises data *Not yet made*

## DB system
- Postgress database
- Shell script for initialisation
