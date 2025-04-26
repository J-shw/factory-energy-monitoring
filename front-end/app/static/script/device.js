function addDevice() {
    const name = document.getElementById('name').value;
    const description = document.getElementById('description').value;

    const connectionType = document.getElementById('connectionType').value;

    const location = document.getElementById('location').value;

    const voltageRating = document.getElementById('voltageRating').value;
    const currentRating = document.getElementById('currentRating').value;

    const highLowVoltage = document.getElementById('highLowVoltage').checked;
    const overCurrent = document.getElementById('overCurrent').checked;
    const powerOutage = document.getElementById('powerOutage').checked;

    const data = {
        name: name,
        description: description,
        connectionType: connectionType,
        location: location,
        voltage: voltageRating,
        currentRatingAmps: currentRating,
        highLowVoltage: highLowVoltage,
        overCurrent: overCurrent,
        powerOutage: powerOutage
    };

    fetch('/add/device', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    })
    .then(result => {
        document.getElementById('response').innerHTML = '<p style="color: green;">Device added successfully!</p>' + JSON.stringify(result);
    })
    .catch(error => {
        if (error instanceof Response) {
            error.json().then(errorData => {
                document.getElementById('response').innerHTML = '<p style="color: red;">Error adding device: ' + JSON.stringify(errorData) + '</p>';
            });
        }
        else {
            document.getElementById('response').innerHTML = '<p style="color: red;">Network error: ' + error + '</p>';
        }
    });
}