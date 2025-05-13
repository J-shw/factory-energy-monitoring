let currentForm = 'iot';
const selectElement = document.getElementById('selectConfig');

function loadIots(selectElement) {
    let iotsList = null
    fetch('/get/iot')
    .then(response => {
        if (!response.ok) {
        throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Iot data:', data);
        iotsList = data;

        iotsList.forEach(iot => {
            let option = document.createElement('option')
            option.value = iot.id;
            option.textContent = iot.name;
            selectElement.appendChild(option);
        });


    })
    .catch(error => {
        console.error('Failed to fetch iot data:', error);
    });
}
function loadEntities() {
    let entitiesList = null
    fetch('/get/entity')
    .then(response => {
        if (!response.ok) {
        throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Entity data:', data);
        entitiesList = data;

        entitiesList.forEach(entity => {
            let option = document.createElement('option')
            option.value = entity.id;
            option.textContent = entity.name;
            selectElement.appendChild(option);
        });


    })
    .catch(error => {
        console.error('Failed to fetch entity data:', error);
    });
}

function fillIotForm(id) {
    fetch('/get/iot/' + id)
    .then(response => {
        if (!response.ok) {
        throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Iot data:', data);
        document.getElementById('name').value = data.name;
        document.getElementById('description').value = data.description;
        document.getElementById('location').value = data.location;
        document.getElementById('measureVoltage').checked = data.voltage;
        document.getElementById('measureCurrent').checked = data.current;
        document.getElementById('connectionType').value = data.protocol;
    })
    .catch(error => {
        console.error('Failed to fetch iot data:', error);
    });
}

function fillEntityForm(id) {
    fetch('/get/entity/' + id)
    .then(response => {
        if (!response.ok) {
        throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Entity data:', data);
        document.getElementById('name').value = data.name;
        document.getElementById('description').value = data.description;
        document.getElementById('location').value = data.location;
        document.getElementById('voltageRating').value = data.voltageRating;
        document.getElementById('currentRating').value = data.currentRating;
        document.getElementById('highLowVoltage').checked = data.highLowVoltage;
        document.getElementById('overCurrent').checked = data.overCurrent;
        document.getElementById('powerOutage').checked = data.powerOutage;
        document.getElementById('upperVoltageLimit').value = data.highVoltageValue;
        document.getElementById('lowerVoltageLimit').value = data.lowVoltageValue;
        document.getElementById('upperCurrentLimit').value = data.overCurrentValue;
        document.getElementById('voltageIotId').value = data.voltageIotId;
        document.getElementById('currentIotId').value = data.currentIotId;


    })
    .catch(error => {
        console.error('Failed to fetch entity data:', error);
    });
}

function gatherDeviceData() {
    let formData = {};
    let id = selectElement.value;
    console.log(currentForm)
  
    if(currentForm == 'iot'){
      formData = {
          "name": document.getElementById('name').value,
          "description": document.getElementById('description').value,
          "protocol": document.getElementById('connectionType').value,
          "location": document.getElementById('location').value,
          "voltage": document.getElementById('measureVoltage').checked,
          "current": document.getElementById('measureCurrent').checked
      };
      addIot(id, formData);
    } else if(currentForm == 'entity'){
      formData = {
          "name": document.getElementById('name').value,
          "description": document.getElementById('description').value,
          "location": document.getElementById('location').value,
          "voltageRating": document.getElementById('voltageRating').value,
          "currentRating": document.getElementById('currentRating').value,
          "highLowVoltage": document.getElementById('highLowVoltage').checked,
          "overCurrent": document.getElementById('overCurrent').checked,
          "powerOutage": document.getElementById('powerOutage').checked,
          "highVoltageValue": document.getElementById('upperVoltageLimit').value,
          "lowVoltageValue": document.getElementById('lowerVoltageLimit').value,
          "overCurrentValue": document.getElementById('upperCurrentLimit').value,
          "voltageIotId": document.getElementById('voltageIotId').value,
          "currentIotId": document.getElementById('currentIotId').value
      };
      addEntity(id, formData);
    }
}

function addIot(id, formData) {
    console.log(id);
    console.log(formData);

    fetch('/create/iot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    })
    .then(result => {
        document.getElementById('response').innerHTML = '<p style="color: green;">Iot added successfully!</p>' + JSON.stringify(result);
    })
    .catch(error => {
        if (error instanceof Response) {
            error.json().then(errorData => {
                document.getElementById('response').innerHTML = '<p style="color: red;">Error adding iot: ' + JSON.stringify(errorData) + '</p>';
            });
        }
        else {
            document.getElementById('response').innerHTML = '<p style="color: red;">Network error: ' + error + '</p>';
        }
    });
}

function addEntity(id, formData) {
    console.log(id);
    console.log(formData);

    fetch('/create/entity', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw response;
        }
        return response.json();
    })
    .then(result => {
        document.getElementById('response').innerHTML = '<p style="color: green;">Entity added successfully!</p>' + JSON.stringify(result);
    })
    .catch(error => {
        if (error instanceof Response) {
            error.json().then(errorData => {
                document.getElementById('response').innerHTML = '<p style="color: red;">Error adding entity: ' + JSON.stringify(errorData) + '</p>';
            });
        }
        else {
            document.getElementById('response').innerHTML = '<p style="color: red;">Network error: ' + error + '</p>';
        }
    });
}

function displayConfigForm(form) {
    currentForm = form;

    formContent = document.getElementById('configForm');
    formContent.innerHTML = '';
    selectElement.innerHTML = '';

    document.getElementById(form+'_view_btn').classList.add('highlight');

    let htmlToInsert = `
        <label for="name">Name:</label>
        <input type="text" id="name" name="name" required>
    
        <label for="description">Description:</label>
        <input type="text" id="description" name="description">
    
        <label for="location">Location:</label>
        <input type="text" id="location" name="location">
        `

    if(form == 'iot'){
        document.getElementById('entity_view_btn').classList.remove('highlight');
        const newOption = document.createElement('option');
        newOption.value = 'new';
        newOption.textContent = 'New IoT';
        selectElement.appendChild(newOption);

        htmlToInsert += `
            <label for="connectionType">Connection Type:</label>
            <select id="connectionType" name="connectionType" required>
                <option value="opc">OPC</option>
                <option value="mqtt">MQTT</option>
            </select>

            <div class="group">
                <label for="measureVoltage">Measures Voltage:</label>
                <input type="checkbox" id="measureVoltage" name="measureVoltage">
                <label for="measureCurrent">Measures Current:</label>
                <input type="checkbox" id="measureCurrent" name="measureCurrent">
            </div>
        
            <button type="button" onclick="gatherDeviceData()">Add IoT</button>
        `;
        formContent.innerHTML = htmlToInsert;
        loadIots(selectElement);
    }
    else if(form == 'entity'){
        document.getElementById('iot_view_btn').classList.remove('highlight');
        const newOption = document.createElement('option');
        newOption.value = 'new';
        newOption.textContent = 'New Entity';
        selectElement.appendChild(newOption);

        htmlToInsert += `
            <div class="group">
                <label for="voltageRating">Voltage Rating (V):</label>
                <input type="number" id="voltageRating" name="voltageRating">
                <label for="currentRating">Current Rating (A):</label>
                <input type="number" id="currentRating" name="currentRating">
            </div>

            <div class="group">
                <label for="upperVoltageLimit">Upper Voltage Limit (V):</label>
                <input type="number" id="upperVoltageLimit" name="upperVoltageLimit">
                <label for="lowerVoltageLimit">Lower Voltage Limit (V):</label>
                <input type="number" id="lowerVoltageLimit" name="lowerVoltageLimit">
                <label for="upperCurrentLimit">Upper Current Limit (A):</label>
                <input type="number" id="upperCurrentLimit" name="upperCurrentLimit">
            </div>

            <div class="group">
                <label for="voltageIotId">Voltage Iot Id:</label>
                <select id ="voltageIotId" name="voltageIotId"></select>
                <label for="currentIotId">Current Iot Id:</label>
                <select id ="currentIotId" name="currentIotId"></select>
            </div>

            <div class="group">
                <label for="highLowVoltage">Monitor Voltage:</label>
                <input type="checkbox" id="highLowVoltage" name="highLowVoltage">
                <label for="overCurrent">Monitor Current:</label>
                <input type="checkbox" id="overCurrent" name="overCurrent">
                <label for="powerOutage">Monitor Power:</label>
                <input type="checkbox" id="powerOutage" name="powerOutage">
            </div>
        
            <button type="button" onclick="gatherDeviceData()">Add Entity</button>
        `;
        formContent.innerHTML = htmlToInsert;
        loadIots(document.getElementById('voltageIotId'));
        loadIots(document.getElementById('currentIotId'));
        loadEntities();
    }
}

selectElement.addEventListener('change', (event) => {
    if( currentForm == 'iot'){
        fillIotForm(event.target.value);
    } else if(currentForm == 'entity'){
        fillEntityForm(event.target.value);
    }
});

displayConfigForm('iot');