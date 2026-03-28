"""
Country Info Service — uses RestCountries API (no API key required)
Returns flag, currency, capital, region for a given country name.
"""
import httpx
from typing import Optional, Dict

_cache: dict = {}


def get_country_info(country_name: str) -> Optional[Dict]:
    """
    Returns country metadata dict or None if not found.
    Fields: name, flag_url, flag_emoji, currency_symbol, currency_name,
            capital, region, languages
    """
    key = country_name.lower().strip()
    if key in _cache:
        return _cache[key]

    try:
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        params = {"fields": "name,flags,currencies,languages,capital,region,cca2"}

        with httpx.Client(timeout=8.0) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            results = resp.json()

        # Pick the best match (prefer exact common name)
        match = None
        for r in results:
            if r.get("name", {}).get("common", "").lower() == key:
                match = r
                break
        if not match and results:
            match = results[-1]  # last result is usually the primary country

        if not match:
            return None

        # Extract currencies
        currencies = match.get("currencies", {})
        currency_code = next(iter(currencies), "")
        currency_info = currencies.get(currency_code, {})

        # Extract languages
        langs = list(match.get("languages", {}).values())

        info = {
            "name":            match["name"]["common"],
            "flag_url":        match["flags"].get("png", ""),
            "flag_emoji":      _cca2_to_flag_emoji(match.get("cca2", "")),
            "currency_symbol": currency_info.get("symbol", ""),
            "currency_name":   currency_info.get("name", ""),
            "currency_code":   currency_code,
            "capital":         (match.get("capital") or [""])[0],
            "region":          match.get("region", ""),
            "languages":       langs[:3],  # top 3
        }
        _cache[key] = info
        return info

    except Exception as e:
        print(f"[country_service] lookup failed for '{country_name}': {e}")
        return None


def _cca2_to_flag_emoji(cca2: str) -> str:
    """Convert 2-letter country code to flag emoji (e.g. 'IN' → '🇮🇳')."""
    if len(cca2) != 2:
        return ""
    return "".join(chr(0x1F1E0 + ord(c) - ord("A")) for c in cca2.upper())
