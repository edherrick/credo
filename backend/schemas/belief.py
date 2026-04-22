import uuid

from pydantic import BaseModel


class BeliefOut(BaseModel):
    id: uuid.UUID
    title: str
    statement: str
    category: str
    source: str | None
    canonical: bool


class CredoBeliefOut(BaseModel):
    belief: BeliefOut
    display_order: int
    notes: str | None
