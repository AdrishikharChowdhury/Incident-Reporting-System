from enum import Enum


class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in progress"
    RESOLVED = "resolved"
    DUPLICATE = "duplicate"
    CLOSED = "closed"
    REJECTED = "rejected"


class GeocodeStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
