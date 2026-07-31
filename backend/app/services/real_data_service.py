import httpx
from typing import List, Dict
from app.services.geo_service import geocode_city

_hotel_cache: Dict[str, List[str]] = {}
_matrix_cache: Dict[str, Dict] = {}

def fetch_real_hotels(destination: str, limit: int = 5) -> List[str]:
    """
    Fetch real hotels in the destination using OpenStreetMap Overpass API.
    To make it ultra-fast, we cache the results per destination.
    """
    key = destination.lower().strip()
    if key in _hotel_cache:
        return _hotel_cache[key]

    # Find the lat/lon of the destination first
    coords = geocode_city(destination)
    if not coords:
        fallback = ["Local Boutique Hotel", "City Center Inn", "Grand Plaza Hotel"]
        _hotel_cache[key] = fallback
        return fallback

    lat, lon = coords
    # Overpass QL: find up to 15 hotels within 10km of the center
    query = f"""
    [out:json][timeout:10];
    node["tourism"="hotel"](around:10000,{lat},{lon});
    out 15;
    """
    url = "https://overpass-api.de/api/interpreter"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, data=query, headers={"User-Agent": "AI-Travel-Copilot/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                hotels = []
                for element in data.get("elements", []):
                    name = element.get("tags", {}).get("name")
                    if name and name not in hotels:
                        hotels.append(name)
                
                if hotels:
                    result = hotels[:limit]
                    _hotel_cache[key] = result
                    return result
    except Exception as e:
        print(f"[real_data_service] Overpass API error for {destination}: {e}")

    fallback = ["Local Boutique Hotel", "City Center Inn", "Grand Plaza Hotel"]
    _hotel_cache[key] = fallback
    return fallback


def get_distance_matrix(coords_list: List[tuple]) -> tuple:
    """
    Fetch real driving distances and times using OSRM Table API.
    Input: List of (lat, lon)
    Returns: (distances_matrix_km, durations_matrix_minutes) or (None, None) on failure
    """
    if len(coords_list) < 2:
        return None, None
        
    # OSRM expects lon,lat format for coordinates
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in coords_list])
    cache_key = coords_str
    
    if cache_key in _matrix_cache:
        return _matrix_cache[cache_key]
        
    url = f"http://router.project-osrm.org/table/v1/driving/{coords_str}?annotations=distance,duration"
    
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, headers={"User-Agent": "AI-Travel-Copilot/1.0"})
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "Ok":
                    # Distances are in meters, convert to km
                    distances = [[val / 1000.0 for val in row] for row in data["distances"]]
                    # Durations are in seconds, convert to minutes
                    durations = [[val / 60.0 for val in row] for row in data["durations"]]
                    
                    _matrix_cache[cache_key] = (distances, durations)
                    return distances, durations
    except Exception as e:
        print(f"[real_data_service] OSRM API error: {e}")
        
    return None, None
