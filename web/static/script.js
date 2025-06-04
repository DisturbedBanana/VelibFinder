// Global variables
let stations = [];
const API_BASE_URL = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    refreshData();
    
    // Add enter key listener to search input
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchStations();
        }
    });
});

// Fetch and display all stations
async function refreshData() {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/stations`);
        stations = await response.json();
        displayStations(stations);
    } catch (error) {
        console.error('Error fetching stations:', error);
        alert('Failed to fetch stations data');
    }
    showLoading(false);
}

// Search stations by name
async function searchStations() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        refreshData();
        return;
    }

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/stations/search/${encodeURIComponent(query)}`);
        const filteredStations = await response.json();
        displayStations(filteredStations);
    } catch (error) {
        console.error('Error searching stations:', error);
        alert('Failed to search stations');
    }
    showLoading(false);
}

// Display stations in the table
function displayStations(stationsToDisplay) {
    const tableBody = document.getElementById('stationsTable');
    tableBody.innerHTML = '';

    stationsToDisplay.forEach(station => {
        const row = document.createElement('tr');
        row.className = 'station-row';
        row.onclick = () => showStationDetails(station);

        const isActive = station.is_installed && station.is_renting;
        const statusClass = isActive ? 'status-active' : 'status-inactive';
        const statusText = isActive ? 'Active' : 'Inactive';

        row.innerHTML = `
            <td>${station.name}</td>
            <td>${station.ebike || 0}</td>
            <td>${station.mechanical || 0}</td>
            <td class="${statusClass}">${statusText}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="event.stopPropagation(); showStationDetails(${JSON.stringify(station)})">
                    Details
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// Show station details in modal
function showStationDetails(station) {
    const modalBody = document.getElementById('stationDetails');
    const isActive = station.is_installed && station.is_renting;
    
    // Create bike lists
    const ebikes = station.bikes?.filter(bike => bike.type === 'E-Bike') || [];
    const mechanical = station.bikes?.filter(bike => bike.type === 'Mechanical') || [];
    
    modalBody.innerHTML = `
        <div class="bike-info">
            <h5>${station.name}</h5>
            <div class="mb-3">
                <span class="status-indicator ${isActive ? 'active' : 'inactive'}"></span>
                Status: ${isActive ? 'Active' : 'Inactive'}
            </div>
            <div class="row">
                <div class="col-md-6">
                    <h6>E-Bikes (${ebikes.length})</h6>
                    <div class="bike-list">
                        ${ebikes.map(bike => `
                            <div class="bike-item">
                                Bike #${bike.number} - ${bike.status}
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="col-md-6">
                    <h6>Mechanical Bikes (${mechanical.length})</h6>
                    <div class="bike-list">
                        ${mechanical.map(bike => `
                            <div class="bike-item">
                                Bike #${bike.number} - ${bike.status}
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <strong>Total Capacity:</strong> ${(station.ebike || 0) + (station.mechanical || 0)}/${station.capacity || 0} bikes
            </div>
            ${station.coordonnees_geo ? `
                <div class="mt-2">
                    <strong>Location:</strong> ${station.coordonnees_geo.lat}, ${station.coordonnees_geo.lon}
                </div>
            ` : ''}
        </div>
    `;

    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('stationModal'));
    modal.show();
}

// Show/hide loading indicator
function showLoading(show) {
    const loadingElement = document.getElementById('loading');
    loadingElement.classList.toggle('d-none', !show);
} 