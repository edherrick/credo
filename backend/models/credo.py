import uuid

from sqlalchemy import TIMESTAMP, Boolean, Date, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.user import Base


class Credo(Base):
    __tablename__ = "credos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    wikidata_id: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class CredoEntity(Base):
    """Junction: entity appears in a credo with a context-specific impact score."""

    __tablename__ = "credo_entities"

    credo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credos.id", ondelete="CASCADE"), primary_key=True
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )
    impact_score: Mapped[int] = mapped_column(Integer, nullable=False)


class EntityEvent(Base):
    """A specific documented action by an entity that affected a metric."""

    __tablename__ = "entity_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    metric_id: Mapped[str | None] = mapped_column(Text, ForeignKey("metrics.id"), nullable=True)
    event_impact_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(Text, nullable=False, default="manual")
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False, default=1.0)
    reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
