import uuid

from sqlalchemy import TIMESTAMP, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.user import Base


class AgendaGeography(Base):
    __tablename__ = "agenda_geographies"

    agenda_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agendas.id", ondelete="CASCADE"), primary_key=True
    )
    geography_id: Mapped[str] = mapped_column(
        Text, ForeignKey("geographies.id", ondelete="CASCADE"), primary_key=True
    )


class AgendaMeans(Base):
    __tablename__ = "agenda_means"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agenda_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agendas.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class Agenda(Base):
    __tablename__ = "agendas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    metric_id: Mapped[str | None] = mapped_column(Text, ForeignKey("metrics.id"), nullable=True)
    credo_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("credos.id"), nullable=True
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
