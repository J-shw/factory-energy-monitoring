function initializeChart() {
    // Amps Chart
    const ampsCtx = document.getElementById('ampsChart').getContext('2d');
    ampsChart = new Chart(ampsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Amps',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second'
                    }
                }
            }
        }
    });

    // Volts Chart
    const voltsCtx = document.getElementById('voltsChart').getContext('2d');
    voltsChart = new Chart(voltsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Volts',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'second'
                    }
                }
            }
        }
    });
}


function updateAmpsChart(payload) {
    if (ampsChart && payload.timestamp && payload.amps) {
        const timestamp = new Date(payload.timestamp);
        ampsChart.data.labels.push(timestamp);
        ampsChart.data.datasets[0].data.push(payload.amps);

        const maxDataPoints = 20;
        if (ampsChart.data.labels.length > maxDataPoints) {
            ampsChart.data.labels.shift();
            ampsChart.data.datasets[0].data.shift();
        }

        ampsChart.update();
    }
}

function updateVoltsChart(payload) {
    if (voltsChart && payload.timestamp && payload.volts) {
        const timestamp = new Date(payload.timestamp);
        voltsChart.data.labels.push(timestamp);
        voltsChart.data.datasets[0].data.push(payload.volts);

        const maxDataPoints = 20;
        if (voltsChart.data.labels.length > maxDataPoints) {
            voltsChart.data.labels.shift();
            voltsChart.data.datasets[0].data.shift();
        }

        voltsChart.update();
    }
}