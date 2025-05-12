let currentForm = 'iot';

function loadIots() {
}
function loadEntities() {
}

function gatherDeviceData() {
    let formData = {};
    let id = document.getElementById('selectConfig').value;
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
          "upperVoltageLimit": document.getElementById('upperVoltageLimit').value,
          "lowerVoltageLimit": document.getElementById('lowerVoltageLimit').value,
          "upperCurrentLimit": document.getElementById('upperCurrentLimit').value
      };
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
    currentForm = form;

    formContent = document.getElementById('configForm');
    selectContent = document.getElementById('selectConfig');
    formContent.innerHTML = '';
    selectContent.innerHTML = '';

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
        newOption.value = '';
        newOption.textContent = 'New IoT';
        selectContent.appendChild(newOption);

        htmlToInsert += `
        <label for="connectionType">Connection Type:</label>
        <select id="connectionType" name="connectionType" required>
            <option value="opc">OPC</option>
            <option value="mqtt">MQTT</option>
        </select>
    
        <label for="measureVoltage">Measures Voltage:</label>
        <input type="checkbox" id="measureVoltage" name="measureVoltage">
        <label for="measureCurrent">Measures Current:</label>
        <input type="checkbox" id="measureCurrent" name="measureCurrent">
    
        <button type="button" onclick="gatherDeviceData()">Add IoT</button>
      `;
      formContent.innerHTML = htmlToInsert;
    }
    else if(form == 'entity'){
        document.getElementById('iot_view_btn').classList.remove('highlight');
        const newOption = document.createElement('option');
        newOption.value = '';
        newOption.textContent = 'New Entity';
        selectContent.appendChild(newOption);

        htmlToInsert += `    
        <label for="voltageRating">Voltage Rating (V):</label>
        <input type="number" id="voltageRating" name="voltageRating">
        <label for="currentRating">Current Rating (A):</label>
        <input type="number" id="currentRating" name="currentRating">

        <label for="upperVoltageLimit">Upper Voltage Limit (V):</label>
        <input type="number" id="upperVoltageLimit" name="upperVoltageLimit">
        <label for="lowerVoltageLimit">Lower Voltage Limit (V):</label>
        <input type="number" id="lowerVoltageLimit" name="lowerVoltageLimit">
        <label for="upperCurrentLimit">Upper Current Limit (A):</label>
        <input type="number" id="upperCurrentLimit" name="upperCurrentLimit">
    
        <label for="highLowVoltage">Monitor Voltage:</label>
        <input type="checkbox" id="highLowVoltage" name="highLowVoltage">
        <label for="overCurrent">Monitor Current:</label>
        <input type="checkbox" id="overCurrent" name="overCurrent">
        <label for="powerOutage">Monitor Power:</label>
        <input type="checkbox" id="powerOutage" name="powerOutage">
    
        <button type="button" onclick="gatherDeviceData()">Add Entity</button>
      `;
      formContent.innerHTML = htmlToInsert;

    }
}

displayConfigForm('iot');