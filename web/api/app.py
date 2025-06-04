from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add the parent directory to the path so we can import the VelibFetcher
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from velib_fetcher import VelibFetcher

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/stations', methods=['GET'])
def get_stations():
    fetcher = VelibFetcher()
    data = fetcher.get_stations()
    if data and "results" in data:
        return jsonify(data["results"])
    return jsonify({"error": "Failed to fetch data"}), 500

@app.route('/api/stations/search/<query>', methods=['GET'])
def search_stations(query):
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

if __name__ == '__main__':
    app.run(debug=True) 