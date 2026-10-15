from typing import Optional, cast

from geopy.geocoders import Nominatim
from geopy.location import Location as Loc

from incident_api.models import Category, GeocodeStatus, Location, Tag


def build_location(display_name: str, incident_id=None) -> Location:
    lat, lon = lat_long(display_name)
    return Location(
        incident_id=incident_id,
        display_name=display_name,
        normalized_name="-".join(
            part.strip() for part in display_name.lower().split(",")
        ),
        latitude=lat,
        longitude=lon,
        geocode_status=(
            GeocodeStatus.SUCCESS if lat is not None else GeocodeStatus.FAILED
        ),
    )


def lat_long(my_location: str) -> tuple[float | None, float | None]:
    geolocator = Nominatim(user_agent="incident-api")

    try:
        location = cast(Optional[Loc], geolocator.geocode(my_location))
    except Exception:
        return None, None

    if location is not None:
        return (location.latitude, location.longitude)
    return None, None


def create_category(category: str) -> Category:
    return Category(name=category, slug="-".join(category.lower().split()))


def create_tags(tag: str) -> Tag:
    return Tag(name=tag, tag="-".join(tag.lower().split()))  


def delete_fields(arr, target):
    for idx, item in enumerate(arr):
        if item["incident_id"] == target:
            arr.pop(idx)
    return arr
