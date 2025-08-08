import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import glob

# Load environment variables
load_dotenv()

class VelibFetcher:
    def __init__(self):
        # Main API endpoint for station status
        self.base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
        # Additional endpoint for detailed bike information
        self.bikes_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-emplacement-des-stations/records"
        self.api_key = os.getenv("VELIB_API_KEY")  # Optional API key

    def cleanup_old_files(self):
        """Delete old JSON files"""
        try:
            # Find all velib data files
            old_files = glob.glob("velib_data_*.json")
            for file in old_files:
                os.remove(file)
                print(f"Deleted old file: {file}")
        except Exception as e:
            print(f"Error cleaning up old files: {e}")

    def get_stations(self, limit=100):
        """
        Fetch Velib stations data
        :param limit: Number of stations to fetch
        :return: List of stations with their data
        """
        try:
            params = {
                "limit": limit,
                "select": "stationcode,name,capacity,ebike,mechanical,is_installed,is_renting,is_returning,coordonnees_geo"
            }
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            print("\n📡 Fetching Velib data...")
            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Generate individual bike information for each station
            print("Generating individual bike information...")
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
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding JSON response: {e}")
            return None

    def get_bike_details(self):
        """
        Generate individual bike information based on station data
        Since the bike details API doesn't provide individual bike info,
        we'll create bike entries based on the station's bike counts
        :return: Dictionary mapping station codes to their bikes
        """
        try:
            # Use the existing station data to create bike information
            # We'll get this data from the main stations call
            station_bikes = {}
            
            # Get the station data from the main API call
            params = {
                "limit": 1000,  # Get all stations
            }
            
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if "results" not in data:
                return None

            # Process the bike data
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
                
                station_bikes[station_code] = bike_list

            return station_bikes
        except Exception as e:
            print(f"Error generating bike details: {e}")
            return None

    def save_to_json(self, data, filename=None):
        """
        Save the fetched data to a JSON file
        :param data: Data to save
        :param filename: Optional custom filename
        """
        if data is None:
            print("❌ No data to save!")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"velib_data_{timestamp}.json"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")

    def print_station_info(self, station):
        """Print formatted information about a station"""
        print(f"\n🚲 Station: {station.get('name', 'Unknown')}")
        print(f"   Code: {station.get('stationcode', 'Unknown')}")
        print(f"   Capacity: {station.get('capacity', 0)}")
        print(f"   E-bikes: {station.get('ebike', 0)}")
        print(f"   Mechanical bikes: {station.get('mechanical', 0)}")
        print(f"   Status: {'🟢' if station.get('is_installed') else '🔴'} Installed")
        print(f"   Renting: {'🟢' if station.get('is_renting') else '🔴'}")
        print(f"   Returning: {'🟢' if station.get('is_returning') else '🔴'}")

def main():
    fetcher = VelibFetcher()
    
    # Clean up old files
    print("🧹 Cleaning up old files...")
    fetcher.cleanup_old_files()
    
    # Fetch data
    data = fetcher.get_stations()
    
    if data and "results" in data:
        stations = data["results"]
        print(f"\n📊 Found {len(stations)} stations")
        
        # Calculate totals
        total_ebikes = sum(station.get("ebike", 0) for station in stations)
        total_mechanical = sum(station.get("mechanical", 0) for station in stations)
        
        print(f"\n📈 Summary:")
        print(f"   Total e-bikes: {total_ebikes}")
        print(f"   Total mechanical bikes: {total_mechanical}")
        print(f"   Total bikes: {total_ebikes + total_mechanical}")
        
        # Save to file
        fetcher.save_to_json(data)
        
        # Print first 3 stations as example
        print("\n🔍 Sample stations:")
        for station in stations[:3]:
            fetcher.print_station_info(station)
            
    else:
        print("❌ No station data found in the response")

if __name__ == "__main__":
    main() 