const deviceCharts = {};
let currentIoTId = null;

function createIotChart(iotId) {
    const charts = document.getElementById('iot-charts');
    charts.innerHTML = '';

    const collection = document.createElement('div');
    collection.classList.add('collection');

    const ampChartContainer = document.createElement('div');
    const voltsChartContainer = document.createElement('div');

    const ampsCanvas = document.createElement('canvas');
    ampsCanvas.id = `ampsChart-${iotId}`;
    ampChartContainer.classList.add('chart-container');
    ampChartContainer.appendChild(ampsCanvas);

    const voltsCanvas = document.createElement('canvas');
    voltsCanvas.id = `voltsChart-${iotId}`;
    voltsChartContainer.classList.add('chart-container');
    voltsChartContainer.appendChild(voltsCanvas);

    collection.appendChild(ampChartContainer);
    collection.appendChild(voltsChartContainer)

    charts.appendChild(collection);

    const ampsCtx = ampsCanvas.getContext('2d');
    const voltsCtx = voltsCanvas.getContext('2d');

    const ampsChart = new Chart(ampsCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Amps', data: [], borderColor: 'rgb(75, 192, 192)', borderWidth: 2, tension: 0.3, pointRadius: 0, fill: false, shadowColor: 'rgba(0, 0, 0, 0.2)', shadowOffsetX: 2, shadowOffsetY: 2, shadowBlur: 4, }] },
        options: { plugins: { legend: { display: false } }, scales: { x: {type: 'time', time: {unit: 'second', tooltipFormat: 'YYYY-MM-DD HH:mm:ss', displayFormats: { second: 'HH:mm:ss', minute: 'HH:mm', hour: 'HH:00', day: 'YYYY-MM-DD' } }, title: { display: true, text: 'Time' } }, y: { beginAtZero: true, title: { display: true, text: 'Amps (A)' } } } }
    });

    const voltsChart = new Chart(voltsCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Volts', data: [], borderColor: 'rgb(255, 99, 132)', borderWidth: 2, tension: 0.3, pointRadius: 0, fill: false, shadowColor: 'rgba(0, 0, 0, 0.2)', shadowOffsetX: 2, shadowOffsetY: 2, shadowBlur: 4, }] },
        options: { plugins: { legend: { display: false } }, scales: { x: {type: 'time', time: {unit: 'second', tooltipFormat: 'YYYY-MM-DD HH:mm:ss', displayFormats: { second: 'HH:mm:ss', minute: 'HH:mm', hour: 'HH:00', day: 'YYYY-MM-DD' } }, title: { display: true, text: 'Time' } }, y: { beginAtZero: true, title: { display: true, text: 'Volts (V)' } } } }
    });

    // Store charts in the deviceCharts object
    deviceCharts[iotId] = { ampsChart, voltsChart };

}

function updateIotCharts(payload) {
    const iotId = payload['iotId'];
    const iotSelect = document.getElementById('iot-select');

    console.log(iotId)
    if (iotSelect.value == iotId) {
        const { ampsChart, voltsChart } = deviceCharts[iotId];

        ampsChart.data.labels.push(payload.timestamp);
        ampsChart.data.datasets[0].data.push(payload.amps);
        ampsChart.update();
    
        voltsChart.data.labels.push(payload.timestamp);
        voltsChart.data.datasets[0].data.push(payload.volts);
        voltsChart.update();
    }
}