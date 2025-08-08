from flask import Flask, jsonify, render_template
from flask_cors import CORS
import sys
import os
import requests
import json
from datetime import datetime

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
            
            response = requests.get(self.base_url, params=params)
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

app = Flask(__name__, template_folder='../templates', static_folder='../static')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return render_template('index.html')

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
    app.run(debug=True) 