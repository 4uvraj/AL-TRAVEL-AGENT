"""
Image Service — fetches destination images from Wikipedia REST API (no API key needed).
Returns image URLs for any city, attraction, or place name.
"""
import httpx
from typing import Optional, Dict

_cache: Dict[str, str] = {}

# High-quality curated fallback images (Unsplash permanent URLs)
# These are carefully chosen to be bright, vibrant city/travel images so the UI looks stunning even if Wikipedia fails.
FALLBACK_IMAGES = {
    "beach": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&h=600&fit=crop",
    "mountain": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1200&h=600&fit=crop",
    "city": "https://images.unsplash.com/photo-1449844908441-8829872d2607?w=1200&h=600&fit=crop", # Vibrant city
    "temple": "https://images.unsplash.com/photo-1515542622106-78bda8cd447e?w=1200&h=600&fit=crop", # Bright temple
    "default": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1200&h=600&fit=crop", # Bright travel landscape
}


def get_destination_image(query: str) -> Optional[str]:
    """Fetch a Wikipedia thumbnail image URL for a destination or place."""
    if not query:
        return FALLBACK_IMAGES["default"]
    
    key = query.lower().strip()
    if key in _cache:
        return _cache[key]

    try:
        # Wikipedia requires proper Title Case for its API
        safe_query = query.title().replace(' ', '_')
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_query}"
        
        # Wikipedia API strictly requires a valid User-Agent with contact info or browser string
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        with httpx.Client(timeout=5.0, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                img = data.get("thumbnail", {}).get("source")
                if img:
                    # Get higher resolution by modifying the width parameter
                    img = img.replace("/60px-", "/800px-").replace("/50px-", "/800px-")
                    _cache[key] = img
                    return img
            else:
                print(f"[image_service] Wikipedia returned {resp.status_code} for {safe_query}")
    except Exception as e:
        print(f"[image_service] fetch failed for '{query}': {e}")

    # Fallback by category keywords
    lower = query.lower()
    for keyword, url in FALLBACK_IMAGES.items():
        if keyword in lower:
            _cache[key] = url
            return url
    
    _cache[key] = FALLBACK_IMAGES["default"]
    return FALLBACK_IMAGES["default"]


def get_place_images(places: list, destination: str = "") -> Dict[str, str]:
    """Fetch images for multiple places, returns {place_name: image_url}."""
    result = {}
    for place in places[:8]:  # Limit to avoid too many API calls
        name = place if isinstance(place, str) else place.get("name", "")
        if name:
            img = get_destination_image(f"{name} {destination}".strip())
            if not img:
                img = get_destination_image(name)
            result[name] = img or FALLBACK_IMAGES["default"]
    return result
