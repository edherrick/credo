import uuid

from sqlalchemy import TIMESTAMP, Boolean, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.user import Base


class Issue(Base):
    """Shared library of abstract policy areas (e.g. Housing Affordability)."""

    __tablename__ = "issues"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(Text, nullable=True)
    canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    author_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class IssueBelief(Base):
    """Junction: which foundational beliefs an issue operationalises."""

    __tablename__ = "issue_beliefs"

    issue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("issues.id"), primary_key=True
    )
    belief_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("beliefs.id"), primary_key=True
    )


class AgendaGeography(Base):
    __tablename__ = "agenda_geographies"

    agenda_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agendas.id", ondelete="CASCADE"), primary_key=True
    )
    geography_id: Mapped[str] = mapped_column(
        Text, ForeignKey("geographies.id", ondelete="CASCADE"), primary_key=True
    )


class MeansCategory(Base):
    __tablename__ = "means_categories"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    family: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Means(Base):
    __tablename__ = "means"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[str] = mapped_column(
        Text, ForeignKey("means_categories.id"), nullable=False
    )
    canonical: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    category: Mapped[MeansCategory] = relationship("MeansCategory", lazy="selectin")
    evidence: Mapped[list["MeansEvidence"]] = relationship(
        "MeansEvidence", lazy="selectin"
    )


class MeansEvidence(Base):
    __tablename__ = "means_evidence"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    means_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("means.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    geography_id: Mapped[str | None] = mapped_column(
        Text, ForeignKey("geographies.id"), nullable=True
    )
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class AgendaMeans(Base):
    __tablename__ = "agenda_means"

    agenda_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agendas.id", ondelete="CASCADE"), primary_key=True
    )
    means_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("means.id", ondelete="RESTRICT"), primary_key=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    means: Mapped[Means] = relationship("Means", lazy="selectin")


class Agenda(Base):
    __tablename__ = "agendas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    metric_id: Mapped[str | None] = mapped_column(Text, ForeignKey("metrics.id"), nullable=True)
    credo_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("credos.id"), nullable=True
    )
    issue_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("issues.id"), nullable=True
    )
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    target_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    target_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    geographies: Mapped[list[AgendaGeography]] = relationship(
        "AgendaGeography", lazy="selectin"
    )
