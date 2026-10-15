from contextlib import asynccontextmanager
from datetime import datetime
from random import randint
from typing import Any
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request, Response, status
from sqlmodel import Session, select

from incident_api import SessionDep, create_db_and_tables, engine
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
from incident_api.models import Categories, Incident, Location, Metadata, Tags
from incident_api.response_model import (
    CategoriesResponse,
    IncidentResponse,
    IncidentsResponse,
    LocationsResponse,
    MetadataResponse,
    TagsResponse,
)
from incident_api.seed import seed
from incident_api.utils import create_category, create_tags, delete_fields, lat_long


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed(session)

    yield


app = FastAPI(root="/api/v1", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello welcome to the incident-reporting-api"}


@app.get("/incidents", response_model=IncidentsResponse)
async def read_incidents(session: SessionDep):
    incidents = session.exec(select(Incident)).all()
    return {"incidents": incidents}


@app.get("/categories", response_model=CategoriesResponse)
async def read_categories(session: SessionDep):
    categories = session.exec(select(Categories)).all()
    return {"categories": categories}


@app.get("/locations", response_model=LocationsResponse)
async def read_locations(session: SessionDep):
    locations = session.exec(select(Location)).all()
    return {"locations": locations}


@app.get("/incident-tags", response_model=TagsResponse)
async def read_incident_tags(session: SessionDep):
    incident_tags = session.exec(select(Tags)).all()
    return {"incident_tags": incident_tags}


@app.get("/submission-data", response_model=MetadataResponse)
async def read_submission_data(session: SessionDep):
    metadata = session.exec(select(Metadata)).all()
    return {"submission-data": metadata}


@app.get("/incidents/{incident_id}",response_model=IncidentResponse)
async def read_a_incident(incident_id: UUID, session: SessionDep):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404)

    category = session.get(Categories, incident.categories_id)
    location = session.get(Location, incident.location_id)
    tags = session.exec(select(Tags).where(Tags.incident_id == incident.id)).first()
    metadata = session.exec(
        select(Metadata).where(Metadata.incident_id == incident.id)
    ).first()
    return {
        "incident": incident,
        "category": category,
        "location": location,
        "tags": tags,
        "metadata": metadata,
    }


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
