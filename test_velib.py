import requests

def test_velib_api():
    print("Testing Velib API connection...")
    
    # The API endpoint
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records"
    
    # Basic parameters to get just one station
    params = {
        "limit": 1,
        "select": "stationcode,name"
    }
    
    try:
        print("Making request to Velib API...")
        response = requests.get(url, params=params)
        
        # Print the status code
        print(f"Status code: {response.status_code}")
        
        # Print the response headers
        print("\nResponse headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
        
        # Try to get the JSON response
        try:
            data = response.json()
            print("\nResponse data:")
            print(data)
            print("\nTest successful! The API is accessible.")
        except Exception as e:
            print(f"\nError parsing JSON response: {e}")
            print("\nRaw response:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")

if __name__ == "__main__":
    test_velib_api() 