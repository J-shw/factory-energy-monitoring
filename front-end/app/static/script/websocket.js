const socket = io('', transports=['websocket']);

socket.on('connect', function() {
    console.log('Connected to server');
});
socket.on('disconnect', function() {
    console.log('Disconnected from server');
});


socket.on('iot_message', function(data) {
    console.log('Received message:')
    console.log(data)

     try {
        const payload = JSON.parse(data.payload);
        updateIotCharts(payload);
    } catch (error) {
        console.error('Error parsing payload:', error);
    }
});

function sendMessage() {
    socket.emit('web-message', 'From the web!');
}