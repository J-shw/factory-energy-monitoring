const deviceCharts = {};

function createDeviceChart(deviceId) {
    let deviceName = 'None'
    
    fetch('/devices/' + deviceId)
    .then(response => {
        if (!response.ok) {
        throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        deviceName = data.name;
        console.log(deviceName);

        const charts = document.getElementById('charts');
        const deviceArea = document.createElement('div');
        deviceArea.id = `deviceArea-${deviceId}`;

        const ampChartContainer = document.createElement('div');
        const voltsChartContainer = document.createElement('div');

        const ampsCanvas = document.createElement('canvas');
        ampsCanvas.id = `ampsChart-${deviceId}`;
        ampChartContainer.classList.add('chart-container');
        ampChartContainer.appendChild(ampsCanvas);

        const voltsCanvas = document.createElement('canvas');
        voltsCanvas.id = `voltsChart-${deviceId}`;
        voltsChartContainer.classList.add('chart-container');
        voltsChartContainer.appendChild(voltsCanvas);

        const title = document.createElement('h2');
        title.textContent = deviceName;

        deviceArea.appendChild(title);
        deviceArea.appendChild(ampChartContainer);
        deviceArea.appendChild(voltsChartContainer);

        charts.appendChild(deviceArea);

        const ampsCtx = ampsCanvas.getContext('2d');
        const voltsCtx = voltsCanvas.getContext('2d');

        const ampsChart = new Chart(ampsCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Amps', data: [], borderColor: 'rgb(75, 192, 192)', borderWidth: 2, tension: 0.3, pointRadius: 0, fill: false, shadowColor: 'rgba(0, 0, 0, 0.2)', shadowOffsetX: 2, shadowOffsetY: 2, shadowBlur: 4, }] },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'Amps (A)' } } } }
        });

        const voltsChart = new Chart(voltsCtx, {
            type: 'line',
            data: { labels: [], datasets: [{ label: 'Volts', data: [], borderColor: 'rgb(255, 99, 132)', borderWidth: 2, tension: 0.3, pointRadius: 0, fill: false, shadowColor: 'rgba(0, 0, 0, 0.2)', shadowOffsetX: 2, shadowOffsetY: 2, shadowBlur: 4, }] },
            options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'Volts (V)' } } } }
        });

        // Store charts in the deviceCharts object
        deviceCharts[deviceId] = { ampsChart, voltsChart };
    })
    .catch(error => {
        console.error('Failed to fetch device data:', error);
    });
}

function updateDeviceCharts(payload) {
    const deviceId = payload.deviceId;
    console.log(deviceId)

    if (!deviceCharts[deviceId]) {
        createDeviceChart(deviceId);
    }

    const { ampsChart, voltsChart } = deviceCharts[deviceId];

    ampsChart.data.labels.push(payload.timestamp);
    ampsChart.data.datasets[0].data.push(payload.amps);
    ampsChart.update();

    voltsChart.data.labels.push(payload.timestamp);
    voltsChart.data.datasets[0].data.push(payload.volts);
    voltsChart.update();
}