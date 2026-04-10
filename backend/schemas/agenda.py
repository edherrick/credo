import datetime
import uuid

from pydantic import BaseModel


class AgendaMeansOut(BaseModel):
    id: uuid.UUID
    category: str
    title: str
    description: str | None
    target: str | None


class AgendaOut(BaseModel):
    id: uuid.UUID
    title: str
    metric_id: str | None
    credo_id: uuid.UUID | None
    geography_ids: list[str]
    direction: str
    target_value: float | None
    target_date: datetime.date | None
    status: str
    means: list[AgendaMeansOut]
