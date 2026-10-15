from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request
from sqlmodel import Session, select

from incident_api import SessionDep, create_db_and_tables, engine
from incident_api.models import (
    Categories,
    Incident,
    IncidentCreate,
    IncidentUpdate,
    Location,
    Metadata,
    StatusUpdate,
    Tags,
)
from incident_api.response_model import (
    IncidentResponse,
    Response,
)
from incident_api.seed import seed
from incident_api.utils import (
    build_location,
    create_category,
    create_tags,
    update_status,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        seed(session)

    yield


app = FastAPI(root_path="/api/v1", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello welcome to the incident-reporting-api"}


@app.get("/incidents", response_model=Response[list[Incident]])
async def read_incidents(session: SessionDep):
    incidents = session.exec(select(Incident)).all()
    return {"data": incidents}


@app.get("/categories", response_model=Response[list[Categories]])
async def read_categories(session: SessionDep):
    categories = session.exec(select(Categories)).all()
    return {"data": categories}


@app.get("/locations", response_model=Response[list[Location]])
async def read_locations(session: SessionDep):
    locations = session.exec(select(Location)).all()
    return {"data": locations}


@app.get("/incident-tags", response_model=Response[list[Tags]])
async def read_incident_tags(session: SessionDep):
    incident_tags = session.exec(select(Tags)).all()
    return {"data": incident_tags}


@app.get("/submission-data", response_model=Response[list[Metadata]])
async def read_submission_data(session: SessionDep):
    metadata = session.exec(select(Metadata)).all()
    return {"data": metadata}


@app.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse[Incident, Categories, Location, Tags, Metadata],
)
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


@app.post(
    "/incidents/create",
    response_model=IncidentResponse[Incident, Categories, Location, Tags, Metadata],
)
async def create_incident(body: IncidentCreate, request: Request, session: SessionDep):

    newId = uuid4()
    rawTags = body.tags or ""
    cleaned_tags = (
        [t.strip() for t in rawTags.split(",") if t.strip()] if rawTags else []
    )
    newTags = Tags(tags=[create_tags(c) for c in cleaned_tags], incident_id=newId)

    locationName = body.location or ""
    newLocation = build_location(locationName, newId)

    rawCategories = body.categories or ""
    category_list = (
        [cat.strip() for cat in rawCategories.split(",")] if rawCategories else []
    )
    newCategories = Categories(
        incident_id=newId, categories=[create_category(c) for c in category_list]
    )

    category_id = newCategories.id
    location_id = newLocation.id
    newIncident = Incident(
        id=newId,
        title=body.title,
        sanitized_text=body.text,
        categories_id=category_id,
        location_id=location_id,
        occurred_at=body.occurred_at,
    )

    newSubMetadata = Metadata(
        incident_id=newId,
        source=request.headers.get("user-agent") or "",
        request_id=uuid4(),
    )

    session.add(newTags)
    session.add(newLocation)
    session.add(newCategories)
    session.add(newIncident)
    session.add(newSubMetadata)
    session.commit()

    return {
        "incident": newIncident,
        "category": newCategories,
        "location": newLocation,
        "tags": newTags,
        "metadata": newSubMetadata,
    }


@app.put(
    "/incidents/update/{incident_id}",
    response_model=IncidentResponse[Incident, Categories, Location, Tags, Metadata],
)
async def update_incident(incident_id: UUID, body: IncidentUpdate, session: SessionDep):
    incident = session.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    category = session.get(Categories, incident.categories_id)
    location = session.get(Location, incident.location_id)
    tags = session.exec(select(Tags).where(Tags.incident_id == incident.id)).first()
    metadata = session.exec(
        select(Metadata).where(Metadata.incident_id == incident.id)
    ).first()

    incident.title = body.title
    incident.sanitized_text = body.text
    session.add(incident)
    session.commit()
    session.refresh(incident)

    return {
        "incident": incident,
        "category": category,
        "location": location,
        "tags": tags,
        "metadata": metadata,
    }


@app.delete("/incidents/{incident_id}", status_code=204)
async def delete_incident(incident_id: UUID, session: SessionDep):
    incident = session.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    category = session.get(Categories, incident.categories_id)
    location = session.get(Location, incident.location_id)
    tags = session.exec(select(Tags).where(Tags.incident_id == incident.id)).first()
    metadata = session.exec(
        select(Metadata).where(Metadata.incident_id == incident.id)
    ).first()

    session.delete(incident)
    session.delete(category)
    session.delete(location)
    session.delete(tags)
    session.delete(metadata)
    session.commit()


@app.put(
    "/incidents/status/{incident_id}",
    status_code=202,
    response_model=Response[Incident],
)
async def status_update(incident_id: UUID, session: SessionDep, body: StatusUpdate):
    incident = session.get(Incident, incident_id)

    if not incident:
        raise HTTPException(status_code=404)

    status = update_status(body.status)

    if status is None:
        raise HTTPException(status_code=400)

    incident.status = status

    session.add(incident)
    session.commit()
    session.refresh(incident)

    return {"data": incident}
