from pydantic.main import BaseModel

from incident_api.models import Categories, Incident, Location, Metadata, Tags


class IncidentsResponse(BaseModel):
    incidents: list[Incident]


class CategoriesResponse(BaseModel):
    categories: list[Categories]


class LocationsResponse(BaseModel):
    locations: list[Location]


class TagsResponse(BaseModel):
    incident_tags: list[Tags]


class MetadataResponse(BaseModel):
    metadata: list[Metadata]


class IncidentResponse(BaseModel):
    incident: Incident
    category: Categories
    location: Location
    tags: Tags
    metadata: Metadata
