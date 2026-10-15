from typing import Generic, TypeVar

from pydantic.main import BaseModel

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")
X = TypeVar("X")


class Response(BaseModel, Generic[T]):
    data: T


class IncidentResponse(BaseModel, Generic[T, U, V, W, X]):
    incident: T
    category: U
    location: V
    tags: W
    metadata: X
