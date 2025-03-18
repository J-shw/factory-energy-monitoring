const socket = io('http://' + document.domain + ':8000', transports=['websocket']);

socket.on('connect', function() {
    console.log('Connected to server');
});
socket.on('disconnect', function() {
    console.log('Disconnected from server');
});


socket.on('mqtt_message', function(data) {
    console.log('Received message: ' + data.topic + ' ' + data.payload)
    const messages = document.getElementById('messages');
    const newMessage = document.createElement('li');
    newMessage.textContent = `Topic: ${data.topic}, Payload: ${data.payload}`;
    messages.appendChild(newMessage);

     try {
        const payload = JSON.parse(data.payload);
        console.log(payload)
        updateDeviceCharts(payload);
    } catch (error) {
        console.error('Error parsing payload:', error);
    }
});

function sendMessage() {
    socket.emit('web-message', 'From the web!');
}