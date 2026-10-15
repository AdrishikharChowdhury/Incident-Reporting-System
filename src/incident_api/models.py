from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy.types import TypeDecorator
from sqlmodel import Field, SQLModel

from incident_api.enums import GeocodeStatus, Status


class Category(SQLModel):
    name: str
    slug: str


class CategoryList(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return [
            item.model_dump() if isinstance(item, Category) else item for item in value
        ]

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return [Category(**item) if isinstance(item, dict) else item for item in value]


class Tag(SQLModel):
    name: str
    tag: str


class TagList(TypeDecorator):
    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return [item.model_dump() if isinstance(item, Tag) else item for item in value]

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return [Tag(**item) if isinstance(item, dict) else item for item in value]


class Incident(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    sanitized_text: str = Field(index=True)
    categories_id: UUID | None = Field(default=None, foreign_key="categories.id")
    location_id: UUID | None = Field(default=None, foreign_key="location.id")
    occurred_at: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    status: Status = Field(
        default=Status.PENDING,
        sa_column=Column(
            SAEnum(
                Status,
                values_callable=lambda enum: [member.value for member in enum],
                native_enum=False,
                length=20,
            ),
            index=True,
            nullable=False,
        ),
    )
    duplicate_of_id: UUID | None = Field(default=None, foreign_key="incident.id")


class Categories(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    incident_id: UUID | None = Field(default=None, foreign_key="incident.id")
    categories: list[Category] = Field(
        default_factory=list, sa_column=Column(CategoryList)
    )


class Location(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    incident_id: UUID | None = Field(default=None, foreign_key="incident.id")
    display_name: str
    normalized_name: str = Field(index=True)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    geocode_status: GeocodeStatus = Field(
        default=GeocodeStatus.FAILED,
        sa_column=Column(
            SAEnum(
                GeocodeStatus,
                values_callable=lambda enum: [member.value for member in enum],
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
    )


class Tags(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    incident_id: UUID | None = Field(default=None, foreign_key="incident.id")
    tags: list[Tag] = Field(default_factory=list, sa_column=Column(TagList))


class Metadata(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    incident_id: UUID | None = Field(default=None, foreign_key="incident.id")
    source: str = Field(default=None, index=True)
    received_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    request_id: UUID | None = Field(default_factory=uuid4)


class IncidentCreate(SQLModel):
    title: str
    text: str
    location: str
    categories: str | None = None
    tags: str | None = None
    occurred_at: datetime | None = None


class IncidentUpdate(SQLModel):
    title: str
    text: str


class StatusUpdate(SQLModel):
    status: Status
