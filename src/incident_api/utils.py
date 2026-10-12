from typing import Optional, cast

from geopy.geocoders import Nominatim
from geopy.location import Location


def lat_long(my_location: str):
    geolocator = Nominatim(user_agent="incident-api")

    try:
        location = cast(Optional[Location], geolocator.geocode(my_location))
    except Exception:
        return None, None

    if location is not None:
        return (location.latitude, location.longitude)
    return None, None


def create_category(category):
    return {
        "name": category,
        "slug": "-".join(category.lower().split()),
    }


def create_tags(tag):
    return {
        "name": tag,
        "tag": "-".join(tag.lower().split(",")),
    }

def delete_fields(arr,target):
    for idx, item in enumerate(arr):
        if item["incident_id"] == target:
            arr.pop(idx)
    return arr