"""
Geocoding Service — uses Nominatim (OpenStreetMap)
No API key required. Returns lat/lng for any city name.
Respects Nominatim's 1 req/sec policy with a simple cache.
"""
import httpx
import time
from typing import Optional, Tuple

_cache: dict = {}
_last_request_time: float = 0.0


def geocode_city(city: str) -> Optional[Tuple[float, float]]:
    """
    Returns (latitude, longitude) for a given city name.
    Returns None if not found.
    """
    global _last_request_time

    key = city.lower().strip()
    if key in _cache:
        return _cache[key]

    # Respect Nominatim's 1 request/second rate limit
    elapsed = time.time() - _last_request_time
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)

    try:
        headers = {"User-Agent": "AI-Travel-Copilot/1.0 (educational project)"}
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "json", "limit": 1}

        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params, headers=headers)
            _last_request_time = time.time()
            resp.raise_for_status()
            data = resp.json()

        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            _cache[key] = (lat, lon)
            return (lat, lon)
    except Exception as e:
        print(f"[geo_service] geocode failed for '{city}': {e}")

    return None
