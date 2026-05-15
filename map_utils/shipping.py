from fastapi import HTTPException
from math import radians, sin, cos, sqrt, atan2
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_address(address: str):
    headers = {
        "User-Agent": "utility-shipping-app/1.0 frukpinyawat@gmail.com"
    }

    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "th"
    }

    res = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=10
    )

    if res.status_code != 200:
        raise HTTPException(status_code=502, detail="Geocoding failed")

    data = res.json()

    if not data:
        raise HTTPException(status_code=404, detail="Address not found")

    return float(data[0]["lat"]), float(data[0]["lon"])


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calculate_shipping_fee(distance_km: float):
    base_price = 100
    max_distance = 2000
    max_price = 365

    fee = base_price + (
        distance_km / max_distance
    ) * (max_price - base_price)

    fee = min(fee, max_price)

    return round(fee)


def calculate_map_shipping(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float | None = None,
    dest_lon: float | None = None,
    dest_address: str | None = None
):
    if dest_lat is not None and dest_lon is not None:
        final_dest_lat = dest_lat
        final_dest_lon = dest_lon
        destination_type = "coordinate"

    elif dest_address:
        final_dest_lat, final_dest_lon = geocode_address(dest_address)
        destination_type = "address"

    else:
        raise HTTPException(
            status_code=400,
            detail="กรุณาส่ง dest_lat/dest_lon หรือ dest_address"
        )

    distance_km = haversine_km(
        origin_lat,
        origin_lon,
        final_dest_lat,
        final_dest_lon
    )

    shipping_fee = calculate_shipping_fee(distance_km)

    return {
        "origin": {
            "lat": origin_lat,
            "lon": origin_lon
        },
        "destination": {
            "type": destination_type,
            "lat": final_dest_lat,
            "lon": final_dest_lon,
            "address": dest_address
        },
        "distance_km": round(distance_km, 2),
        "shipping_fee": shipping_fee,
        "currency": "THB"
    }