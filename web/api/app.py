from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import os

# Create a simplified VelibFetcher class directly in the app
class VelibFetcher:
    def __init__(self):
        self.base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"

    def get_stations(self, limit=100):
        try:
            params = {
                "limit": limit,
                "select": "stationcode,name,capacity,ebike,mechanical,is_installed,is_renting,is_returning,coordonnees_geo"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Generate individual bike information for each station
            if "results" in data:
                for station in data["results"]:
                    station_code = station.get("stationcode")
                    ebike_count = station.get("ebike", 0)
                    mechanical_count = station.get("mechanical", 0)
                    
                    # Create individual bike entries
                    bike_list = []
                    
                    # Add e-bikes
                    for i in range(ebike_count):
                        bike_info = {
                            "number": f"E{station_code}-{i+1:03d}",
                            "type": "E-Bike",
                            "status": "Available"
                        }
                        bike_list.append(bike_info)
                    
                    # Add mechanical bikes
                    for i in range(mechanical_count):
                        bike_info = {
                            "number": f"M{station_code}-{i+1:03d}",
                            "type": "Mechanical",
                            "status": "Available"
                        }
                        bike_list.append(bike_info)
                    
                    station["bikes"] = bike_list
            
            return data
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/robots.txt')
def robots():
    return 'User-agent: *\nDisallow: /', 200, {'Content-Type': 'text/plain'}

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Velib Station Finder - Lucas Guichard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .station-card { cursor: pointer; transition: transform 0.2s; }
            .station-card:hover { transform: translateY(-2px); }
            .loading { text-align: center; padding: 20px; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="text-center mb-4">🚲 Velib Station Finder</h1>
            
            <!-- Search Bar -->
            <div class="row mb-4">
                <div class="col-md-8 mx-auto">
                    <div class="input-group">
                        <input type="text" id="searchInput" class="form-control" placeholder="Search for a station...">
                        <button class="btn btn-primary" onclick="searchStations()">Search</button>
                        <button class="btn btn-secondary" onclick="refreshData()">Refresh</button>
                    </div>
                </div>
            </div>

            <!-- Loading Indicator -->
            <div id="loading" class="text-center d-none">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>

            <!-- Stations Container -->
            <div id="stationsContainer">
                <div class="loading">Click "Refresh" to load stations</div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            async function refreshData() {
                const loading = document.getElementById('loading');
                const container = document.getElementById('stationsContainer');
                
                loading.classList.remove('d-none');
                container.innerHTML = '';
                
                try {
                    const response = await fetch('/api/stations');
                    const stations = await response.json();
                    displayStations(stations);
                } catch (error) {
                    container.innerHTML = '<div class="alert alert-danger">Error loading stations</div>';
                } finally {
                    loading.classList.add('d-none');
                }
            }
            
            async function searchStations() {
                const query = document.getElementById('searchInput').value;
                if (!query) return refreshData();
                
                const loading = document.getElementById('loading');
                const container = document.getElementById('stationsContainer');
                
                loading.classList.remove('d-none');
                container.innerHTML = '';
                
                try {
                    const response = await fetch(`/api/stations/search/${encodeURIComponent(query)}`);
                    const stations = await response.json();
                    displayStations(stations);
                } catch (error) {
                    container.innerHTML = '<div class="alert alert-danger">Error searching stations</div>';
                } finally {
                    loading.classList.add('d-none');
                }
            }
            
            function displayStations(stations) {
                const container = document.getElementById('stationsContainer');
                
                if (stations.length === 0) {
                    container.innerHTML = '<div class="alert alert-info">No stations found</div>';
                    return;
                }
                
                const stationsHtml = stations.map(station => `
                    <div class="card mb-3 station-card" onclick="showStationDetails('${station.name}')">
                        <div class="card-body">
                            <h5 class="card-title">${station.name}</h5>
                            <p class="card-text">
                                <strong>E-Bikes:</strong> ${station.ebike || 0} | 
                                <strong>Mechanical:</strong> ${station.mechanical || 0}
                            </p>
                            <span class="badge ${station.is_installed && station.is_renting ? 'bg-success' : 'bg-danger'}">
                                ${station.is_installed && station.is_renting ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                    </div>
                `).join('');
                
                container.innerHTML = stationsHtml;
            }
            
            function showStationDetails(stationName) {
                alert('Station details for: ' + stationName + '\\n\\nThis would show individual bike details in a full implementation.');
            }
            
            // Load stations on page load
            refreshData();
        </script>
    </body>
    </html>
    """
    return html_content

@app.route('/test')
def test():
    return jsonify({"status": "ok", "message": "VelibFinder API is working!"})

@app.route('/api/stations', methods=['GET'])
def get_stations():
    try:
        fetcher = VelibFetcher()
        data = fetcher.get_stations()
        if data and "results" in data:
            return jsonify(data["results"])
        return jsonify({"error": "Failed to fetch data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stations/search/<query>', methods=['GET'])
def search_stations(query):
    try:
        fetcher = VelibFetcher()
        data = fetcher.get_stations()
        if data and "results" in data:
            stations = data["results"]
            filtered_stations = [
                station for station in stations
                if query.lower() in station.get("name", "").lower()
            ]
            return jsonify(filtered_stations)
        return jsonify({"error": "Failed to fetch data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 