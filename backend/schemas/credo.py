import uuid

from pydantic import BaseModel

from schemas.agenda import AgendaOut
from schemas.entity import CredoEntityOut


class CredoOut(BaseModel):
    id: uuid.UUID
    username: str
    title: str
    description: str | None
    agendas: list[AgendaOut]
    entities: list[CredoEntityOut]
