function loadEvents(){
    let body = document.getElementById('eventsTableBody');
    fetch('your_api_endpoint_url')
    .then(response => {
        if (!response.ok) {
            if (response.status === 404){
                body.innerHTML="<p style='text-align: center; width: 100%; padding: 20px; font-size: x-large;'>No events found</p>"
            } 
            throw new Error(`HTTP error - status: ${response.status}`);
        }
        return response.json();
        })
        .then(data => {
            console.log(data); // Process the data here
        })
        .catch(error => {
            console.error("Fetch error:", error);
        }
    );
}
loadEvents();