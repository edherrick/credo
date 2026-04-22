import datetime
import uuid

from pydantic import BaseModel


class EntityEventOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    event_date: datetime.date | None
    metric_id: str | None
    event_impact_score: int | None
    source_url: str | None
    source_type: str


class CredoEntityOut(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    description: str | None
    impact_score: int  # credo-specific score from credo_entities
    events: list[EntityEventOut]


class EntityDetailOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str | None
    type: str
    description: str | None
    wikidata_id: str | None
    events: list[EntityEventOut]
