"""Utility module for country geolocation lookups.

Loads country data from a bundled JSON file at module level for fast lookups.
"""

import json
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "static" / "countries.json"

_countries: dict[str, dict] = {}


def _load_countries() -> None:
    """Load the countries.json file into the module-level lookup dict."""
    global _countries
    if _countries:
        return
    if not _DATA_PATH.exists():
        return
    with open(_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        iso3 = entry.get("iso3", "").upper()
        if iso3:
            _countries[iso3] = entry


_load_countries()


def get_centroid(iso3: str) -> tuple[float, float] | None:
    """Return (latitude, longitude) for a country by ISO3 code, or None."""
    entry = _countries.get(iso3.upper())
    if entry is None:
        return None
    lat = entry.get("latitude")
    lon = entry.get("longitude")
    if lat is None or lon is None:
        return None
    return (float(lat), float(lon))


def get_country_name(iso3: str) -> str | None:
    """Return the country name for a given ISO3 code, or None."""
    entry = _countries.get(iso3.upper())
    if entry is None:
        return None
    return entry.get("name")
