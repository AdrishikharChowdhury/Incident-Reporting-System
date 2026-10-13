from sqlmodel import Session, select

from incident_api.data import (
    get_mock_categories,
    get_mock_incident_tags,
    get_mock_incidents,
    get_mock_locations,
    get_mock_submission_metadata,
)
from incident_api.models import Categories, Incident, Location, Metadata, Tags


def seed(session: Session) -> None:
    if session.exec(select(Incident)).first():
        return

    session.add_all([Incident(**row) for row in get_mock_incidents()])
    session.add_all([Categories(**row) for row in get_mock_categories()])
    session.add_all([Location(**row) for row in get_mock_locations()])
    session.add_all([Tags(**row) for row in get_mock_incident_tags()])
    session.add_all([Metadata(**row) for row in get_mock_submission_metadata()])
    session.commit()
