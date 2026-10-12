from datetime import datetime
from random import randint
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response, status

from incident_api.data import (
    IMMUTABLE,
    get_mock_categories,
    get_mock_incident_tags,
    get_mock_incidents,
    get_mock_locations,
    get_mock_submission_metadata,
    set_mock_categories,
    set_mock_incident_tags,
    set_mock_incidents,
    set_mock_locations,
    set_mock_metadata,
)
from incident_api.utils import create_category, create_tags, delete_fields, lat_long

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
incident_id — PK, FK → incidents.id;
tag — part of composite PK;
together, (incident_id, tag) form the composite primary key

=====================
submission_metadata
=====================
submission_id — PK;
incident_id — FK → incidents.id;
source;
received_at;
request_id. Avoid reporter identity unless needed.
"""

app = FastAPI(root_path="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello welcome to the incident-reporting-api"}


@app.get("/incidents")
async def read_incidents():
    return {"incidents": get_mock_incidents()}


@app.get("/categories")
async def read_categories():
    return {"categories": get_mock_categories()}


@app.get("/locations")
async def read_locations():
    return {"locations": get_mock_locations()}


@app.get("/incident-tags")
async def read_incident_tags():
    return {"incident-tags": get_mock_incident_tags()}


@app.get("/submission-data")
async def read_submission_data():
    return {"submission-data": get_mock_submission_metadata()}


@app.get("/incidents/{incident_id}")
async def read_a_incident(incident_id: int):
    incidents = get_mock_incidents()
    categories = get_mock_categories()
    metadata = get_mock_submission_metadata()
    locations = get_mock_locations()
    tags = get_mock_incident_tags()
    req_incident = None
    req_category = None
    req_metadatum = None
    req_location = None
    req_tag = None
    for incident in incidents:
        if incident["id"] == incident_id:
            req_incident = incident

    for category in categories:
        if category["incident_id"] == incident_id:
            req_category = category

    for metadatum in metadata:
        if metadatum["incident_id"] == incident_id:
            req_metadatum = metadatum

    for location in locations:
        if location["incident_id"] == incident_id:
            req_location = location

    for tag in tags:
        if tag["incident_id"] == incident_id:
            req_tag = tag

    if req_incident is not None and (
        req_location is not None
        or req_metadatum is not None
        or req_tag is not None
        or req_category is not None
    ):
        return {
            "incident": req_incident,
            "location": req_location,
            "categories": req_category,
            "incident_tags": req_tag,
            "metadata": req_metadatum,
        }

    raise HTTPException(status_code=404)


@app.post("/incidents/create")
async def create_incident(body: dict[str, Any], request: Request):

    newTagId = randint(100, 1000)
    newLocationId = randint(100, 1000)
    locationName = body.get("location") or ""
    locationLat, locationLong = lat_long(locationName)
    newCategoryId = randint(100, 1000)
    newSubId = randint(100, 1000)
    newId = randint(100, 1000)
    rawCategories = body.get("categories") or ""
    category_list = (
        [cat.strip() for cat in rawCategories.split(",")] if rawCategories else []
    )
    rawTags = body.get("tags") or ""
    cleaned_tags = rawTags.strip().split(",") if rawTags else []

    newTags = {
        "id": newTagId,
        "incident_id": newId,
        "tags": list(map(create_tags, cleaned_tags)) if cleaned_tags else [],
    }

    newLocation = {
        "id": newLocationId,
        "incident_id": newId,
        "display_name": locationName,
        "normalized_name": "-".join(
            part.strip() for part in locationName.lower().split(",")
        ),
        "latitude": locationLat,
        "longitude": locationLong,
        "geocode_status": "failed"
        if locationLat is None and locationLong is None
        else "success",
    }

    newCategories = {
        "id": newCategoryId,
        "incident_id": newId,
        "categories": list(map(create_category, category_list))
        if category_list
        else [],
    }

    newIncident = {
        "id": newId,
        "title": body.get("title"),
        "sanitized_text": body.get("text"),
        "category_id": newCategoryId,
        "location_id": newLocationId,
        "occurred_at": body.get("occurred_at"),
        "created_at": datetime.now(),
        "status": "pending",
        "duplicate_of_id": None,
    }

    newSubMetadata = {
        "id": newSubId,
        "incident_id": newId,
        "source": request.headers.get("user-agent"),
        "received_at": datetime.now(),
        "request_id": f"req_uuid_{randint(100, 10000)}c",
    }

    get_mock_categories().append(newCategories)
    get_mock_incidents().append(newIncident)
    get_mock_locations().append(newLocation)
    get_mock_incident_tags().append(newTags)
    get_mock_submission_metadata().append(newSubMetadata)

    return {
        "incident": newIncident,
        "location": newLocation,
        "categories": newCategories,
        "incident_tags": newTags,
        "metadata": newSubMetadata,
    }


@app.put("/incidents/update/{incident_id}")
async def update_incident(incident_id: int, body: dict[str, Any], response: Response):
    incidents = get_mock_incidents()
    incident = next((i for i in incidents if i["id"] == incident_id), None)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not body:
        raise HTTPException(status_code=400, detail="Nothing to update")

    ignored = sorted(IMMUTABLE & body.keys())
    applied = {key: value for key, value in body.items() if key not in IMMUTABLE}

    if not applied:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Immutable Fields",
                "message": "You cant change these fields, try changing other fields",
                "fields": ignored,
            },
        )

    for key, value in applied.items():
        incident[key] = value

    set_mock_incidents(incidents)

    if ignored:
        response.status_code = status.HTTP_207_MULTI_STATUS

    return {"new_incident": incident, "ignored_fields": ignored}


@app.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: int):
    incidents = get_mock_incidents()
    locations = get_mock_locations()
    categories = get_mock_categories()

    metadata = delete_fields(get_mock_submission_metadata(), incident_id)
    tags = delete_fields(get_mock_incident_tags(), incident_id)

    for idx, incident in enumerate(incidents):
        if incident["id"] == incident_id:
            categories = delete_fields(categories, incident["category_id"])
            locations = delete_fields(locations, incident["location_id"])
            incidents.pop(idx)
            set_mock_categories(categories)
            set_mock_incident_tags(tags)
            set_mock_incidents(incidents)
            set_mock_locations(locations)
            set_mock_metadata(metadata)

            return Response(status_code=204, content="Incident has been deleted")

    raise HTTPException(status_code=404)
