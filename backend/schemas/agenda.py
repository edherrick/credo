import datetime
import uuid

from pydantic import BaseModel


class AgendaOut(BaseModel):
    id: uuid.UUID
    title: str
    metric_id: str | None
    geography_id: str | None
    direction: str
    target_value: float | None
    target_date: datetime.date | None
    status: str

    model_config = {"from_attributes": True}
