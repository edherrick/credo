import uuid

from pydantic import BaseModel

from schemas.agenda import AgendaOut
from schemas.belief import CredoBeliefOut
from schemas.entity import CredoEntityOut


class CredoSummaryOut(BaseModel):
    id: uuid.UUID
    username: str
    title: str
    description: str | None
    created_at: str


class CredoOut(BaseModel):
    id: uuid.UUID
    username: str
    title: str
    description: str | None
    beliefs: list[CredoBeliefOut]
    agendas: list[AgendaOut]
    entities: list[CredoEntityOut]
