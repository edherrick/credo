import uuid

from sqlalchemy import TIMESTAMP, Boolean, Date, ForeignKey, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.user import Base


class Credo(Base):
    __tablename__ = "credos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # NB: `username` is the credo's public handle (the /credo/<username> slug),
    # not the owner's account username. owner_id is the link to the owning user.
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
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


class CredoSubscription(Base):
    """Junction: a user follows a credo.

    Self-membership write shape — distinct from the owner-scoped `get_owned_credo`
    pattern. Any authenticated user may follow any credo; the user acts only on
    their own row (PK is the (user, credo) pair, so following is idempotent).
    """

    __tablename__ = "credo_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    credo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credos.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class UserBelief(Base):
    """Junction: a user's personal collection of beliefs they endorse.

    Self-membership write shape (same as `credo_subscriptions`): the user toggles
    only their own row, no ownership check. A saved belief can later be *promoted*
    into a credo the user owns via the `credo_beliefs` junction.
    """

    __tablename__ = "user_beliefs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    belief_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("beliefs.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Belief(Base):
    """Shared library of foundational principles and philosophical axioms."""

    __tablename__ = "beliefs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class CredoBelief(Base):
    """Junction: which beliefs a credo holds, in what order, with what emphasis."""

    __tablename__ = "credo_beliefs"

    credo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credos.id", ondelete="CASCADE"), primary_key=True
    )
    belief_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("beliefs.id"), primary_key=True
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    belief: Mapped["Belief"] = relationship("Belief", lazy="selectin")


class AgendaBelief(Base):
    """Junction: which foundational beliefs an agenda operationalises."""

    __tablename__ = "agenda_beliefs"

    agenda_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agendas.id", ondelete="CASCADE"), primary_key=True
    )
    belief_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("beliefs.id"), primary_key=True
    )


class Axis(Base):
    """Shared library of evaluation dimensions for entity scoring."""

    __tablename__ = "axes"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    family: Mapped[str] = mapped_column(Text, nullable=False)
    canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class CredoAxis(Base):
    """Junction: which axes a credo uses to evaluate entities, and how heavily."""

    __tablename__ = "credo_axes"

    credo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credos.id", ondelete="CASCADE"), primary_key=True
    )
    axis_id: Mapped[str] = mapped_column(Text, ForeignKey("axes.id"), primary_key=True)
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    axis: Mapped["Axis"] = relationship("Axis", lazy="selectin")


class CredoEntityScore(Base):
    """Per-axis entity score within a credo. Replaces credo_entities.impact_score in Phase 2+."""

    __tablename__ = "credo_entity_scores"

    credo_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("credos.id", ondelete="CASCADE"), primary_key=True
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True
    )
    axis_id: Mapped[str] = mapped_column(Text, ForeignKey("axes.id"), primary_key=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


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
