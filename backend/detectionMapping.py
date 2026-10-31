import requests
import json

def get_true_global_soil_profile():
    """
    Detects global coordinates (lat/lon) via IP and queries a global 
    geospatial data source for real soil metrics anywhere in the world.
    """
    try:
        # Here we Fetch location details including latitude and longitude
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get("https://ipapi.co/json/", headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        city = data.get("city", "Unknown City")
        country = data.get("country_name", "Unknown Country")
        lat = data.get("latitude")
        lon = data.get("longitude")
        
        print(f"[*] Detected Location: {city}, {country} (Lat: {lat}, Lon: {lon})")
        
        if lat is None or lon is None:
            raise ValueError("Coordinates could not be resolved from IP.")

        #Query a global soil/environmental API using coordinates
        soilgrids_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}&property=phh2o&property=soc&depth=0-5cm&value=mean"
        
        soil_response = requests.get(soilgrids_url, headers=headers, timeout=10)
        
        if soil_response.status_code == 200:
            soil_data = soil_response.json()
            # Extract pH or other metrics returned by the global grid
            layers = soil_data.get("properties", {}).get("layers", [])
            
            ph_val = None
            for layer in layers:
                if layer.get("name") == "phh2o":
                    # SoilGrids returns pH multiplied by 10 for storage efficiency
                    mean_val = layer["depths"][0]["values"]["mean"]
                    ph_val = mean_val / 10.0 if mean_val else 7.0

            soil_profile = {
                "type": "Dynamic Grid-Mapped Soil (Global Coordinates)",
                "pH": ph_val if ph_val else 7.0,
                "fertility": "Derived from Global Geospatial Model",
                "source": "ISRIC SoilGrids 2.0"
            }
        else:
            # Fallback if geospatial API encounters rate-limiting or downtime
            soil_profile = {
                "type": "Standard Regional Loam",
                "pH": 6.8,
                "fertility": "Medium",
                "source": "Local Fallback Estimate"
            }
        
        return {
            "location": {"city": city, "country": country, "latitude": lat, "longitude": lon},
            "soil_profile": soil_profile
        }

    except Exception as e:
        print(f"[!] Geolocation or API error: {e}")
        return {
            "location": {"city": "Global", "country": "Global", "latitude": 0.0, "longitude": 0.0},
            "soil_profile": {"type": "Default Agricultural Soil", "pH": 7.0, "fertility": "Medium"}
        }

if __name__ == "__main__":
    print("---This our AI MODEL BROTHA---")
    result = get_true_global_soil_profile()
    
    print("\n[+] Resulting Data Payload:")
    print(json.dumps(result, indent=4))