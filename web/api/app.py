from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
import requests
import json
from datetime import datetime
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
    # Return a simple 204 No Content response for favicon requests
    return '', 204

@app.route('/robots.txt')
def robots():
    # Return a simple robots.txt
    return 'User-agent: *\nDisallow: /', 200, {'Content-Type': 'text/plain'}

@app.route('/')
def index():
    try:
        # Return a simple HTML response instead of using templates
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VelibFinder</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚲</text></svg>">
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #2b2b2b; color: #e0e0e0; }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 30px; }
                .search-box { margin: 20px 0; text-align: center; }
                input[type="text"] { padding: 10px; width: 300px; border: 1px solid #555; background: #3c3c3c; color: #e0e0e0; }
                button { padding: 10px 20px; background: #5dade2; color: white; border: none; cursor: pointer; }
                .stations { margin-top: 20px; }
                .station { padding: 10px; margin: 5px 0; background: #3c3c3c; border-radius: 5px; cursor: pointer; }
                .station:hover { background: #4a4a4a; }
                .loading { text-align: center; color: #b8b8b8; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚲 VelibFinder</h1>
                    <p>Find Velib stations and bike availability in Paris</p>
                </div>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search for a station...">
                    <button onclick="searchStations()">Search</button>
                    <button onclick="loadStations()">Load All Stations</button>
                </div>
                <div id="stations" class="stations">
                    <div class="loading">Click "Load All Stations" to see available bikes</div>
                </div>
            </div>
            <script>
                async function loadStations() {
                    const stationsDiv = document.getElementById('stations');
                    stationsDiv.innerHTML = '<div class="loading">Loading stations...</div>';
                    
                    try {
                        const response = await fetch('/api/stations');
                        const stations = await response.json();
                        displayStations(stations);
                    } catch (error) {
                        stationsDiv.innerHTML = '<div class="loading">Error loading stations</div>';
                    }
                }
                
                async function searchStations() {
                    const query = document.getElementById('searchInput').value;
                    if (!query) return loadStations();
                    
                    const stationsDiv = document.getElementById('stations');
                    stationsDiv.innerHTML = '<div class="loading">Searching...</div>';
                    
                    try {
                        const response = await fetch(`/api/stations/search/${encodeURIComponent(query)}`);
                        const stations = await response.json();
                        displayStations(stations);
                    } catch (error) {
                        stationsDiv.innerHTML = '<div class="loading">Error searching stations</div>';
                    }
                }
                
                function displayStations(stations) {
                    const stationsDiv = document.getElementById('stations');
                    if (stations.length === 0) {
                        stationsDiv.innerHTML = '<div class="loading">No stations found</div>';
                        return;
                    }
                    
                    stationsDiv.innerHTML = stations.map(station => `
                        <div class="station" onclick="showStationDetails('${station.name}')">
                            <h3>${station.name}</h3>
                            <p>E-Bikes: ${station.ebike || 0} | Mechanical: ${station.mechanical || 0}</p>
                            <p>Status: ${station.is_installed && station.is_renting ? 'Active' : 'Inactive'}</p>
                        </div>
                    `).join('');
                }
                
                function showStationDetails(stationName) {
                    alert('Station details for: ' + stationName + '\\n\\nThis would show individual bike details in a full implementation.');
                }
                
                // Load stations on page load
                loadStations();
            </script>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        return jsonify({"error": f"Template error: {str(e)}"}), 500

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