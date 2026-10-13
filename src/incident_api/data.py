"""
Mock data shaped to the SQLModel models.

Ids are deterministic UUIDs (uuid5) so foreign keys can reference each other
across the modules. Each dict's keys match the corresponding model's fields, so
`Model(**row)` builds the row directly.
"""

from datetime import datetime, timezone
from uuid import NAMESPACE_DNS, uuid5

from incident_api.enums import GeocodeStatus, Status


def _uid(name: str):
    return uuid5(NAMESPACE_DNS, name)


IMMUTABLE = {"category", "categories", "tags", "location"}

_CATEGORIES = [
    {
        "id": _uid("category-1"),
        "incident_id": _uid("incident-2"),
        "categories": [{"name": "Municipal Services", "slug": "municipal-services"}],
    },
    {
        "id": _uid("category-2"),
        "incident_id": _uid("incident-4"),
        "categories": [{"name": "Public Safety", "slug": "public-safety"}],
    },
    {
        "id": _uid("category-3"),
        "incident_id": _uid("incident-1"),
        "categories": [
            {"name": "Utility / Infrastructure", "slug": "utility-infrastructure"}
        ],
    },
    {
        "id": _uid("category-4"),
        "incident_id": _uid("incident-3"),
        "categories": [
            {"name": "Utility / Infrastructure", "slug": "utility-infrastructure"}
        ],
    },
    {
        "id": _uid("category-5"),
        "incident_id": _uid("incident-5"),
        "categories": [{"name": "Sanitation & Waste", "slug": "sanitation-waste"}],
    },
]

_LOCATIONS = [
    {
        "id": _uid("location-2"),
        "incident_id": _uid("incident-2"),
        "display_name": "Park Street, Kolkata",
        "normalized_name": "park-street-kolkata",
        "latitude": 22.5551,
        "longitude": 88.3517,
        "geocode_status": GeocodeStatus.SUCCESS,
    },
    {
        "id": _uid("location-1"),
        "incident_id": _uid("incident-1"),
        "display_name": "Sector V, Salt Lake, Kolkata",
        "normalized_name": "sector-v-salt-lake-kolkata",
        "latitude": 22.5726,
        "longitude": 88.4372,
        "geocode_status": GeocodeStatus.SUCCESS,
    },
    {
        "id": _uid("location-3"),
        "incident_id": _uid("incident-3"),
        "display_name": "Sector V, Salt Lake, Kolkata",
        "normalized_name": "sector-v-salt-lake-kolkata",
        "latitude": 22.5726,
        "longitude": 88.4372,
        "geocode_status": GeocodeStatus.SUCCESS,
    },
    {
        "id": _uid("location-4"),
        "incident_id": _uid("incident-4"),
        "display_name": "Howrah Bridge, Kolkata",
        "normalized_name": "howrah-bridge-kolkata",
        "latitude": 22.5851,
        "longitude": 88.3468,
        "geocode_status": GeocodeStatus.SUCCESS,
    },
    {
        "id": _uid("location-5"),
        "incident_id": _uid("incident-5"),
        "display_name": "Salt Lake Sector II, Kolkata",
        "normalized_name": "salt-lake-sector-ii-kolkata",
        "latitude": 22.58,
        "longitude": 88.41,
        "geocode_status": GeocodeStatus.SUCCESS,
    },
]

_INCIDENTS = [
    {
        "id": _uid("incident-1"),
        "title": "Power Outage in Sector V",
        "sanitized_text": "Sudden grid failure affecting commercial blocks.",
        "categories_id": _uid("category-3"),
        "location_id": _uid("location-1"),
        "occurred_at": datetime(2026, 10, 11, 8, 30, tzinfo=timezone.utc),
        "created_at": datetime(2026, 10, 11, 8, 35, tzinfo=timezone.utc),
        "status": Status.PENDING,
        "duplicate_of_id": None,
    },
    {
        "id": _uid("incident-2"),
        "title": "Water Pipeline Leakage",
        "sanitized_text": "Main supply pipe rupture near the main intersection.",
        "categories_id": _uid("category-1"),
        "location_id": _uid("location-2"),
        "occurred_at": datetime(2026, 10, 11, 7, 10, tzinfo=timezone.utc),
        "created_at": datetime(2026, 10, 11, 7, 20, tzinfo=timezone.utc),
        "status": Status.PENDING,
        "duplicate_of_id": None,
    },
    {
        "id": _uid("incident-3"),
        "title": "Duplicate Power Outage Report",
        "sanitized_text": "Power failure reported again in Sector V block B.",
        "categories_id": _uid("category-4"),
        "location_id": _uid("location-3"),
        "occurred_at": datetime(2026, 10, 11, 8, 32, tzinfo=timezone.utc),
        "created_at": datetime(2026, 10, 11, 8, 40, tzinfo=timezone.utc),
        "status": Status.CLOSED,
        "duplicate_of_id": _uid("incident-1"),
    },
    {
        "id": _uid("incident-4"),
        "title": "Assault Near Howrah Bridge",
        "sanitized_text": "A late-night altercation escalated into an assault near the bridge approach.",
        "categories_id": _uid("category-2"),
        "location_id": _uid("location-4"),
        "occurred_at": datetime(2026, 10, 12, 22, 15, tzinfo=timezone.utc),
        "created_at": datetime(2026, 10, 12, 22, 30, tzinfo=timezone.utc),
        "status": Status.PENDING,
        "duplicate_of_id": None,
    },
    {
        "id": _uid("incident-5"),
        "title": "Illegal Dumping Behind Market",
        "sanitized_text": "Construction debris and household waste dumped behind the market complex.",
        "categories_id": _uid("category-5"),
        "location_id": _uid("location-5"),
        "occurred_at": datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc),
        "created_at": datetime(2026, 10, 12, 9, 20, tzinfo=timezone.utc),
        "status": Status.PENDING,
        "duplicate_of_id": None,
    },
]

_TAGS = [
    {
        "id": _uid("tags-1"),
        "incident_id": _uid("incident-1"),
        "tags": [{"name": "Power Outage", "tag": "power-outage"}],
    },
    {
        "id": _uid("tags-2"),
        "incident_id": _uid("incident-2"),
        "tags": [{"name": "Water Leak", "tag": "water-leak"}],
    },
    {
        "id": _uid("tags-3"),
        "incident_id": _uid("incident-3"),
        "tags": [{"name": "Duplicate Report", "tag": "duplicate-report"}],
    },
    {
        "id": _uid("tags-4"),
        "incident_id": _uid("incident-4"),
        "tags": [{"name": "Assault", "tag": "assault"}],
    },
    {
        "id": _uid("tags-5"),
        "incident_id": _uid("incident-5"),
        "tags": [{"name": "Illegal Dumping", "tag": "illegal-dumping"}],
    },
]

_METADATA = [
    {
        "id": _uid("metadata-1"),
        "incident_id": _uid("incident-1"),
        "source": "mobile_app",
        "received_at": datetime(2026, 10, 11, 8, 34, tzinfo=timezone.utc),
        "request_id": _uid("request-1"),
    },
    {
        "id": _uid("metadata-2"),
        "incident_id": _uid("incident-2"),
        "source": "web_portal",
        "received_at": datetime(2026, 10, 11, 7, 19, tzinfo=timezone.utc),
        "request_id": _uid("request-2"),
    },
    {
        "id": _uid("metadata-3"),
        "incident_id": _uid("incident-3"),
        "source": "mobile_app",
        "received_at": datetime(2026, 10, 11, 8, 39, tzinfo=timezone.utc),
        "request_id": _uid("request-3"),
    },
    {
        "id": _uid("metadata-4"),
        "incident_id": _uid("incident-4"),
        "source": "web_portal",
        "received_at": datetime(2026, 10, 12, 22, 29, tzinfo=timezone.utc),
        "request_id": _uid("request-4"),
    },
    {
        "id": _uid("metadata-5"),
        "incident_id": _uid("incident-5"),
        "source": "mobile_app",
        "received_at": datetime(2026, 10, 12, 9, 18, tzinfo=timezone.utc),
        "request_id": _uid("request-5"),
    },
]


def get_mock_categories():
    return _CATEGORIES


def get_mock_locations():
    return _LOCATIONS


def get_mock_incidents() -> list[dict]:
    return _INCIDENTS


def get_mock_incident_tags():
    return _TAGS


def get_mock_submission_metadata():
    return _METADATA


def set_mock_incidents(incidents):
    global _INCIDENTS
    _INCIDENTS = incidents


def set_mock_metadata(metadata):
    global _METADATA
    _METADATA = metadata


def set_mock_locations(locations):
    global _LOCATIONS
    _LOCATIONS = locations


def set_mock_categories(categories):
    global _CATEGORIES
    _CATEGORIES = categories


def set_mock_incident_tags(incident_tags):
    global _TAGS
    _TAGS = incident_tags
