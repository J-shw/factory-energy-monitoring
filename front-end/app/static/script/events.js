function loadEvents() {
    const eventsTableBody = document.getElementById('eventsTableBody');
    eventsTableBody.innerHTML = '';

    fetch('/get/event/')
        .then(response => {
            if (!response.ok) {
                if (response.status === 404) {
                    eventsTableBody.innerHTML = "<p style='text-align: center; width: 100%; padding: 20px; font-size: x-large;'>No events found</p>";
                    throw new Error('No events found (handled)');
                }
                throw new Error(`HTTP error - status: ${response.status}`);
            }
            return response.json();
        })
        .then(eventsData => {
            const entityFetches = eventsData.map(event =>
                fetch('/get/entity/' + event.entityId)
                .then(response => {
                    if (!response.ok) {
                        console.warn("Failed to find entity for ID:", event.entityId, "Status:", response.status);
                        return null;
                    }
                    return response.json();
                })
                .catch(error => {
                    console.error("Error fetching entity for ID:", event.entityId, error);
                    return null;
                })
            );
            return Promise.all(entityFetches).then(entitiesData => {
                return eventsData.map((event, index) => ({
                    ...event,
                    entity: entitiesData[index]
                }));
            });
        })
        .then(combinedData => {
            combinedData.forEach(row => {
                const rowElement = document.createElement('tr');
                const entityName = row.entity ? row.entity.name : 'Unknown Entity';

                rowElement.innerHTML = `
                    <td>${row.timestamp}</td>
                    <td>${entityName}</td>
                    <td>${row.overCurrent}</td>
                    <td>${row.highLowVoltage}</td>
                `;
                eventsTableBody.appendChild(rowElement);
            });
        })
        .catch(error => {
            if (error.message !== 'No events found (handled)') {
                 console.error("Fetch error:", error);
            }
        });
}

loadEvents();