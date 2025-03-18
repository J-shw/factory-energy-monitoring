function addDevice() {
    const name = document.getElementById('name').value;
    const serial_number = document.getElementById('description').value;

    const data = {
        name: name,
        description: serial_number
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