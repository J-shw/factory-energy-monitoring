let voltsChart = null;
let ampsChart = null;

function initializeCharts() {
    console.log('Initializing charts');

    // Amps Chart
    const ampsCtx = document.getElementById('ampsChart').getContext('2d');
    ampsChart = new Chart(ampsCtx, {
        type: 'line',
        data: {
            labels:[],
            datasets: [{
                label: 'Amps',
                data:[],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Amps (A)'
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
            labels:[],
            datasets: [{
                label: 'Volts',
                data:[],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Volts (V)'
                    }
                }
            }
        }
    });
    console.log('Charts initialized');
}

function updateAmpsChart(payload) {
    console.log('Updating amps chart');
    if (ampsChart && payload.amps) {
        ampsChart.data.labels.push(""); // Push an empty string as label
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
    console.log('Updating volts chart');
    if (voltsChart && payload.volts) {
        voltsChart.data.labels.push(""); // Push an empty string as label
        voltsChart.data.datasets[0].data.push(payload.volts);

        const maxDataPoints = 20;
        if (voltsChart.data.labels.length > maxDataPoints) {
            voltsChart.data.labels.shift();
            voltsChart.data.datasets[0].data.shift();
        }

        voltsChart.update();
    }
}