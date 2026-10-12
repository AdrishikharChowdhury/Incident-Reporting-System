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
        "incident_id": 4,
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
    {
        "id": 5,
        "incident_id": 5,
        "categories": [{"name": "Sanitation & Waste", "slug": "sanitation-waste"}],
    },
]
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
    {
        "id": 21,
        "incident_id": 4,
        "display_name": "Howrah Bridge, Kolkata",
        "normalized_name": "howrah-bridge-kolkata",
        "latitude": 22.5851,
        "longitude": 88.3468,
        "geocode_status": "success",
    },
    {
        "id": 22,
        "incident_id": 5,
        "display_name": "Salt Lake Sector II, Kolkata",
        "normalized_name": "salt-lake-sector-ii-kolkata",
        "latitude": 22.58,
        "longitude": 88.41,
        "geocode_status": "success",
    },
]
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
    {
        "id": 4,
        "title": "Assault Near Howrah Bridge",
        "sanitized_text": "A late-night altercation escalated into an assault near the bridge approach.",
        "category_id": 2,
        "location_id": 21,
        "occurred_at": "2026-10-12T22:15:00Z",
        "created_at": "2026-10-12T22:30:00Z",
        "status": "pending",
        "duplicate_of_id": None,
    },
    {
        "id": 5,
        "title": "Illegal Dumping Behind Market",
        "sanitized_text": "Construction debris and household waste dumped behind the market complex.",
        "category_id": 5,
        "location_id": 22,
        "occurred_at": "2026-10-12T09:05:00Z",
        "created_at": "2026-10-12T09:20:00Z",
        "status": "needs review",
        "duplicate_of_id": None,
    },
]
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
    {
        "id": 67,
        "incident_id": 4,
        "tags": [{"name": "Assault", "tag": "assault"}],
    },
    {
        "id": 78,
        "incident_id": 5,
        "tags": [{"name": "Illegal Dumping", "tag": "illegal-dumping"}],
    },
]
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
    {
        "id": 104,
        "incident_id": 4,
        "source": "web_portal",
        "received_at": "2026-10-12T22:29:00Z",
        "request_id": "req_uuid_77410d",
    },
    {
        "id": 105,
        "incident_id": 5,
        "source": "mobile_app",
        "received_at": "2026-10-12T09:18:00Z",
        "request_id": "req_uuid_55237e",
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
