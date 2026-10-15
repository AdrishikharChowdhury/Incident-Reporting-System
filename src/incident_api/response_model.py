
from typing import Generic, TypeVar

from pydantic.main import BaseModel

from incident_api.models import Categories, Incident, Location, Metadata, Tags

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T

class IncidentResponse(BaseModel):
    incident: Incident
    category: Categories
    location: Location
    tags: Tags
    metadata: Metadata
