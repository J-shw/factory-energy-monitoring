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
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0,
                fill: false,
                shadowColor: 'rgba(0, 0, 0, 0.2)',
                shadowOffsetX: 2,
                shadowOffsetY: 2,
                shadowBlur: 4,
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
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
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 0,
                fill: false,
                shadowColor: 'rgba(0, 0, 0, 0.2)',
                shadowOffsetX: 2,
                shadowOffsetY: 2,
                shadowBlur: 4,
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: false
                }
            },
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

        ampsChart.data.labels.push("");
        ampsChart.data.datasets[0].data.push(payload.amps);

        ampsChart.update();

    }
}

function updateVoltsChart(payload) {
    console.log('Updating volts chart');
    if (voltsChart && payload.volts) {

        voltsChart.data.labels.push("");
        voltsChart.data.datasets[0].data.push(payload.volts);

        voltsChart.update();
    }
}