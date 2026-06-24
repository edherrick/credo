import datetime
import re
import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.agenda import AgendaOut
from schemas.belief import CredoBeliefOut
from schemas.entity import CredoEntityOut

# Public handle / URL slug: 3–40 chars, lowercase alphanumeric + hyphens,
# must start and end with an alphanumeric.
HANDLE_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,38}[a-z0-9])$")

# Handles that would shadow a real route (e.g. /credo/new) or are otherwise reserved.
RESERVED_HANDLES = frozenset(
    {"new", "edit", "create", "login", "register", "logout", "me", "explore",
     "library", "api", "admin", "settings", "credo", "credos"}
)


class CredoSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    title: str
    description: str | None
    owner_id: uuid.UUID | None
    created_at: datetime.datetime


class CredoOut(BaseModel):
    id: uuid.UUID
    username: str
    title: str
    description: str | None
    owner_id: uuid.UUID | None
    beliefs: list[CredoBeliefOut]
    agendas: list[AgendaOut]
    entities: list[CredoEntityOut]


class CredoCreate(BaseModel):
    """Create payload. The owner is taken from the authenticated user, never the body."""

    username: str = Field(..., description="Public handle / URL slug for the credo")
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("username")
    @classmethod
    def validate_handle(cls, v: str) -> str:
        v = v.strip().lower()
        if not HANDLE_RE.match(v):
            raise ValueError(
                "Handle must be 3–40 characters: lowercase letters, numbers, and "
                "hyphens, starting and ending with a letter or number."
            )
        if v in RESERVED_HANDLES:
            raise ValueError(f"'{v}' is a reserved handle — please choose another.")
        return v


class CredoUpdate(BaseModel):
    """Partial update. Only fields present in the request are changed.

    The handle (`username`) and `owner_id` are intentionally not updatable here.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
