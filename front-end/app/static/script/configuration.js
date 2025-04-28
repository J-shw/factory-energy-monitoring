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

function displayConfigForm(form) {
    formContent = document.getElementById('configForm');
    selectContent = document.getElementById('selectConfig');
    formContent.innerHTML = '';
    selectContent.innerHTML = '';

    const htmlToInsert = `
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
    
        <label for="description">Description:</label>
        <input type="text" id="description" name="description">
    
        <label for="location">Location:</label>
        <input type="text" id="location" name="location">
        `

    if(form == 'iot'){
        const newOption = document.createElement('option');
        newOption.value = '';
        newOption.textContent = 'New IoT';
        selectContent.appendChild(newOption);

        htmlToInsert += `
        <label for="connectionType">Connection Type:</label>
        <select id="connectionType" name="connectionType" required>
            <option value="opc">OPC</option>
            <option value="mqtt">MQTT</option>
        </select>
    
        <label for="voltageRating">Voltage Rating (V):</label>
        <input type="number" id="voltageRating" name="voltageRating">
        <label for="currentRating">Current Rating (A):</label>
        <input type="number" id="currentRating" name="currentRating">
    
        <label for="measureVoltage">Measures Voltage:</label>
        <input type="checkbox" id="measureVoltage" name="measureVoltage">
        <label for="measureCurrent">Measures Current:</label>
        <input type="checkbox" id="measureCurrent" name="measureCurrent">
    
        <button type="button" onclick="addDevice()">Add IoT</button>
      `;
      formContent.innerHTML = htmlToInsert;
    }
    else if(form == 'entity'){
        const newOption = document.createElement('option');
        newOption.value = '';
        newOption.textContent = 'New Entity';
        selectContent.appendChild(newOption);

        htmlToInsert += `    
        <label for="voltageRating">Voltage Rating (V):</label>
        <input type="number" id="voltageRating" name="voltageRating">
        <label for="currentRating">Current Rating (A):</label>
        <input type="number" id="currentRating" name="currentRating">
    
        <label for="highLowVoltage">Monitor Voltage:</label>
        <input type="checkbox" id="highLowVoltage" name="highLowVoltage">
        <label for="overCurrent">Monitor Current:</label>
        <input type="checkbox" id="overCurrent" name="overCurrent">
        <label for="powerOutage">Monitor Power:</label>
        <input type="checkbox" id="powerOutage" name="powerOutage">
    
        <button type="button" onclick="addDevice()">Add Entity</button>
      `;
      formContent.innerHTML = htmlToInsert;

    }
}