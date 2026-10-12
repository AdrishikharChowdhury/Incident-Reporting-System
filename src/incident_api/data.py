"""
===========
incidents
===========
id — PK;
title;
sanitized_text;
category_id — FK → categories.id;
location_id — FK → locations.id;
occurred_at;
created_at;
status;
duplicate_of_id — nullable FK → incidents.id

===========
locations
===========
id — PK;
display_name;
normalized_name;
latitude;
longitude;
geocode_status

============
categories
============
id — PK;
name;
slug

===============
incident_tags
===============
id — PK;
incident_id — FK → incidents.id;
tags — list of {name, tag}

=====================
submission_metadata
=====================
submission_id — PK;
incident_id — FK → incidents.id;
source;
received_at;
request_id. Avoid reporter identity unless needed.
"""

IMMUTABLE = {"category", "categories", "tags", "location"}

_CATEGORIES = [
    {
        "id": 1,
        "incident_id": 2,
        "categories": [{"name": "Municipal Services", "slug": "municipal-services"}],
    },
    {
        "id": 2,
        "incident_id": None,
        "categories": [{"name": "Public Safety", "slug": "public-safety"}],
    },
    {
        "id": 3,
        "incident_id": 1,
        "categories": [
            {"name": "Utility / Infrastructure", "slug": "utility-infrastructure"}
        ],
    },
    {
        "id": 4,
        "incident_id": 3,
        "categories": [
            {"name": "Utility / Infrastructure", "slug": "utility-infrastructure"}
        ],
    },
]


def get_mock_categories():
    return _CATEGORIES


_LOCATIONS = [
    {
        "id": 5,
        "incident_id": 2,
        "display_name": "Park Street, Kolkata",
        "normalized_name": "park-street-kolkata",
        "latitude": 22.5551,
        "longitude": 88.3517,
        "geocode_status": "success",
    },
    {
        "id": 12,
        "incident_id": 1,
        "display_name": "Sector V, Salt Lake, Kolkata",
        "normalized_name": "sector-v-salt-lake-kolkata",
        "latitude": 22.5726,
        "longitude": 88.4372,
        "geocode_status": "success",
    },
    {
        "id": 13,
        "incident_id": 3,
        "display_name": "Sector V, Salt Lake, Kolkata",
        "normalized_name": "sector-v-salt-lake-kolkata",
        "latitude": 22.5726,
        "longitude": 88.4372,
        "geocode_status": "success",
    },
]


def get_mock_locations():
    return _LOCATIONS


_INCIDENTS = [
    {
        "id": 1,
        "title": "Power Outage in Sector V",
        "sanitized_text": "Sudden grid failure affecting commercial blocks.",
        "category_id": 3,
        "location_id": 12,
        "occurred_at": "2026-10-11T08:30:00Z",
        "created_at": "2026-10-11T08:35:00Z",
        "status": "pending",
        "duplicate_of_id": None,
    },
    {
        "id": 2,
        "title": "Water Pipeline Leakage",
        "sanitized_text": "Main supply pipe rupture near the main intersection.",
        "category_id": 1,
        "location_id": 5,
        "occurred_at": "2026-10-11T07:10:00Z",
        "created_at": "2026-10-11T07:20:00Z",
        "status": "needs review",
        "duplicate_of_id": None,
    },
    {
        "id": 3,
        "title": "Duplicate Power Outage Report",
        "sanitized_text": "Power failure reported again in Sector V block B.",
        "category_id": 4,
        "location_id": 13,
        "occurred_at": "2026-10-11T08:32:00Z",
        "created_at": "2026-10-11T08:40:00Z",
        "status": "closed",
        "duplicate_of_id": 1,
    },
]


def get_mock_incidents() -> list[dict]:
    return _INCIDENTS


_TAGS = [
    {
        "id": 34,
        "incident_id": 1,
        "tags": [{"name": "Power Outage", "tag": "power-outage"}],
    },
    {
        "id": 43,
        "incident_id": 2,
        "tags": [{"name": "Grid Failure", "tag": "grid-failure"}],
    },
    {"id": 56, "incident_id": 3, "tags": [{"name": "Water Leak", "tag": "water-leak"}]},
]


def get_mock_incident_tags():
    return _TAGS


_METADATA = [
    {
        "id": 101,
        "incident_id": 1,
        "source": "mobile_app",
        "received_at": "2026-10-11T08:34:00Z",
        "request_id": "req_uuid_88192a",
    },
    {
        "id": 102,
        "incident_id": 2,
        "source": "web_portal",
        "received_at": "2026-10-11T07:19:00Z",
        "request_id": "req_uuid_44109b",
    },
    {
        "id": 103,
        "incident_id": 3,
        "source": "mobile_app",
        "received_at": "2026-10-11T08:39:00Z",
        "request_id": "req_uuid_99211c",
    },
]


def get_mock_submission_metadata():
    return _METADATA


def set_mock_incidents(incidents):
    global _INCIDENTS
    _INCIDENTS = incidents
