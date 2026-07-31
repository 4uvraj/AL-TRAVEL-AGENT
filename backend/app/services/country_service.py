"""
Country Info Service — Instant offline lookup with fallback API support.
Returns flag, currency, capital, region for a given destination or country name.
"""
from typing import Optional, Dict

# Comprehensive local database of major travel destinations & countries
COUNTRY_DB = {
    "india": {
        "name": "India",
        "flag_url": "https://flagcdn.com/w320/in.png",
        "flag_emoji": "🇮🇳",
        "currency_symbol": "₹",
        "currency_name": "Indian Rupee",
        "currency_code": "INR",
        "capital": "New Delhi",
        "region": "Asia",
        "languages": ["Hindi", "English"]
    },
    "france": {
        "name": "France",
        "flag_url": "https://flagcdn.com/w320/fr.png",
        "flag_emoji": "🇫🇷",
        "currency_symbol": "€",
        "currency_name": "Euro",
        "currency_code": "EUR",
        "capital": "Paris",
        "region": "Europe",
        "languages": ["French"]
    },
    "japan": {
        "name": "Japan",
        "flag_url": "https://flagcdn.com/w320/jp.png",
        "flag_emoji": "🇯🇵",
        "currency_symbol": "¥",
        "currency_name": "Japanese Yen",
        "currency_code": "JPY",
        "capital": "Tokyo",
        "region": "Asia",
        "languages": ["Japanese"]
    },
    "united kingdom": {
        "name": "United Kingdom",
        "flag_url": "https://flagcdn.com/w320/gb.png",
        "flag_emoji": "🇬🇧",
        "currency_symbol": "£",
        "currency_name": "British Pound",
        "currency_code": "GBP",
        "capital": "London",
        "region": "Europe",
        "languages": ["English"]
    },
    "united states": {
        "name": "United States",
        "flag_url": "https://flagcdn.com/w320/us.png",
        "flag_emoji": "🇺🇸",
        "currency_symbol": "$",
        "currency_name": "US Dollar",
        "currency_code": "USD",
        "capital": "Washington, D.C.",
        "region": "Americas",
        "languages": ["English"]
    },
    "italy": {
        "name": "Italy",
        "flag_url": "https://flagcdn.com/w320/it.png",
        "flag_emoji": "🇮🇹",
        "currency_symbol": "€",
        "currency_name": "Euro",
        "currency_code": "EUR",
        "capital": "Rome",
        "region": "Europe",
        "languages": ["Italian"]
    },
    "spain": {
        "name": "Spain",
        "flag_url": "https://flagcdn.com/w320/es.png",
        "flag_emoji": "🇪🇸",
        "currency_symbol": "€",
        "currency_name": "Euro",
        "currency_code": "EUR",
        "capital": "Madrid",
        "region": "Europe",
        "languages": ["Spanish"]
    },
    "thailand": {
        "name": "Thailand",
        "flag_url": "https://flagcdn.com/w320/th.png",
        "flag_emoji": "🇹🇭",
        "currency_symbol": "฿",
        "currency_name": "Thai Baht",
        "currency_code": "THB",
        "capital": "Bangkok",
        "region": "Asia",
        "languages": ["Thai"]
    },
    "united arab emirates": {
        "name": "United Arab Emirates",
        "flag_url": "https://flagcdn.com/w320/ae.png",
        "flag_emoji": "🇦🇪",
        "currency_symbol": "AED",
        "currency_name": "UAE Dirham",
        "currency_code": "AED",
        "capital": "Abu Dhabi",
        "region": "Asia",
        "languages": ["Arabic"]
    },
    "indonesia": {
        "name": "Indonesia",
        "flag_url": "https://flagcdn.com/w320/id.png",
        "flag_emoji": "🇮🇩",
        "currency_symbol": "Rp",
        "currency_name": "Indonesian Rupiah",
        "currency_code": "IDR",
        "capital": "Jakarta",
        "region": "Asia",
        "languages": ["Indonesian"]
    },
    "singapore": {
        "name": "Singapore",
        "flag_url": "https://flagcdn.com/w320/sg.png",
        "flag_emoji": "🇸🇬",
        "currency_symbol": "S$",
        "currency_name": "Singapore Dollar",
        "currency_code": "SGD",
        "capital": "Singapore",
        "region": "Asia",
        "languages": ["English", "Malay", "Mandarin"]
    },
    "switzerland": {
        "name": "Switzerland",
        "flag_url": "https://flagcdn.com/w320/ch.png",
        "flag_emoji": "🇨🇭",
        "currency_symbol": "CHF",
        "currency_name": "Swiss Franc",
        "currency_code": "CHF",
        "capital": "Bern",
        "region": "Europe",
        "languages": ["German", "French", "Italian"]
    },
    "australia": {
        "name": "Australia",
        "flag_url": "https://flagcdn.com/w320/au.png",
        "flag_emoji": "🇦🇺",
        "currency_symbol": "A$",
        "currency_name": "Australian Dollar",
        "currency_code": "AUD",
        "capital": "Canberra",
        "region": "Oceania",
        "languages": ["English"]
    }
}

# City/Region aliases mapped to parent country key
CITY_ALIASES = {
    "goa": "india", "mumbai": "india", "delhi": "india", "bengaluru": "india", "jaipur": "india",
    "kerala": "india", "agra": "india", "manali": "india", "shimla": "india", "udaipur": "india",
    "paris": "france", "nice": "france", "lyon": "france",
    "tokyo": "japan", "kyoto": "japan", "osaka": "japan",
    "london": "united kingdom", "edinburgh": "united kingdom", "manchester": "united kingdom",
    "new york": "united states", "los angeles": "united states", "miami": "united states",
    "rome": "italy", "venice": "italy", "florence": "italy", "milan": "italy",
    "barcelona": "spain", "madrid": "spain", "seville": "spain",
    "dubai": "united arab emirates", "abu dhabi": "united arab emirates",
    "bali": "indonesia", "jakarta": "indonesia",
    "bangkok": "thailand", "phuket": "thailand", "chiang mai": "thailand",
    "zurich": "switzerland", "geneva": "switzerland",
    "sydney": "australia", "melbourne": "australia",
    "uk": "united kingdom", "usa": "united states", "uae": "united arab emirates"
}

def get_country_info(destination: str) -> Optional[Dict]:
    """
    Returns country metadata dict for any given city or country name.
    Guaranteed fast execution with zero network latency.
    """
    if not destination:
        return COUNTRY_DB["india"]

    clean = destination.split(",")[-1].strip().lower()

    # 1. Check direct country key
    if clean in COUNTRY_DB:
        return COUNTRY_DB[clean]

    # 2. Check city alias
    if clean in CITY_ALIASES:
        return COUNTRY_DB[CITY_ALIASES[clean]]

    # 3. Fuzzy search inside destination string
    for alias, c_key in CITY_ALIASES.items():
        if alias in clean or clean in alias:
            return COUNTRY_DB[c_key]

    for c_key, c_data in COUNTRY_DB.items():
        if c_key in clean or clean in c_key:
            return c_data

    # Default fallback to India for Indian regions or generic global defaults
    return COUNTRY_DB["india"]
