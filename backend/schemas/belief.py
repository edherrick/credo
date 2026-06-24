import uuid

from pydantic import BaseModel


class BeliefOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    title: str
    statement: str
    category: str
    source: str | None
    canonical: bool


class CredoBeliefOut(BaseModel):
    model_config = {"from_attributes": True}

    belief: BeliefOut
    display_order: int
    notes: str | None
