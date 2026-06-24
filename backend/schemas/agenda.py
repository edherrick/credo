import datetime
import uuid

from pydantic import BaseModel


class MeansCategoryOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    label: str
    family: str
    description: str | None


class MeansEvidenceOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    description: str | None
    source_url: str | None
    geography_id: str | None
    outcome: str | None


class MeansOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    description: str | None
    category: MeansCategoryOut
    canonical: bool
    evidence: list[MeansEvidenceOut]


class AgendaMeansOut(BaseModel):
    model_config = {"from_attributes": True}

    means_id: uuid.UUID
    notes: str | None
    means: MeansOut


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
