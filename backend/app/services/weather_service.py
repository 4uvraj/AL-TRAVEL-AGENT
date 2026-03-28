"""
Weather Service — uses Open-Meteo (no API key required)
Returns daily weather forecast for a given lat/lng.
WMO weather interpretation codes mapped to emoji + description.
"""
import httpx
from typing import Optional, List, Dict

# WMO Weather Code → (emoji, description)
WMO_CODES = {
    0:  ("☀️",  "Clear sky"),
    1:  ("🌤️", "Mainly clear"),
    2:  ("⛅",  "Partly cloudy"),
    3:  ("☁️",  "Overcast"),
    45: ("🌫️", "Foggy"),
    48: ("🌫️", "Icy fog"),
    51: ("🌦️", "Light drizzle"),
    53: ("🌦️", "Moderate drizzle"),
    55: ("🌧️", "Dense drizzle"),
    61: ("🌧️", "Slight rain"),
    63: ("🌧️", "Moderate rain"),
    65: ("🌧️", "Heavy rain"),
    71: ("🌨️", "Slight snow"),
    73: ("🌨️", "Moderate snow"),
    75: ("❄️",  "Heavy snow"),
    80: ("🌦️", "Rain showers"),
    81: ("🌧️", "Moderate showers"),
    82: ("⛈️",  "Violent showers"),
    95: ("⛈️",  "Thunderstorm"),
    96: ("⛈️",  "Thunderstorm with hail"),
    99: ("⛈️",  "Thunderstorm with heavy hail"),
}


def get_weather_forecast(lat: float, lon: float, days: int = 7) -> List[Dict]:
    """
    Returns a list of daily weather dicts for the next `days` days.
    Each dict has: date, weather_emoji, weather_desc, temp_max, temp_min
    """
    days = min(days, 16)  # Open-Meteo max is 16 days
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
        "forecast_days": days,
    }
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        daily = data.get("daily", {})
        times = daily.get("time", [])
        codes = daily.get("weather_code", [])
        maxes = daily.get("temperature_2m_max", [])
        mins  = daily.get("temperature_2m_min", [])

        result = []
        for i, date in enumerate(times):
            code = codes[i] if i < len(codes) else 0
            emoji, desc = WMO_CODES.get(code, ("🌡️", "Unknown"))
            result.append({
                "date": date,
                "weather_emoji": emoji,
                "weather_desc": desc,
                "temp_max": round(maxes[i], 1) if i < len(maxes) else None,
                "temp_min": round(mins[i], 1)  if i < len(mins)  else None,
            })
        return result

    except Exception as e:
        print(f"[weather_service] forecast failed: {e}")
        return []
