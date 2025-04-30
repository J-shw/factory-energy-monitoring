const iotSelect = document.getElementById('iot-select');

fetch('/get/iot')
.then(response => {
    if (!response.ok) {
    throw new Error(`HTTP error - status: ${response.status}`);
    }
    return response.json();
})
.then(data => {
    console.log('Iot data:', data);
    data.forEach(iot => {
        let option = document.createElement('option')
        option.value = iot.id;
        option.textContent = iot.name;
        iotSelect.appendChild(option);
    });


})
.catch(error => {
    console.error('Failed to fetch iot data:', error);
});

iotSelect.addEventListener('change', (event) => {
    const iotId = event.target.value;
    currentIoTId = iotId;
    if (currentIoTId == 'empty'){
        document.getElementById('iot-charts').innerHTML = `
        <div class="no-iot">
            No IoT selected
        </div>
        `
    }
    else{
        console.log('New iot selected with ID - ', iotId);
        createIotChart(iotId)
    }
  });