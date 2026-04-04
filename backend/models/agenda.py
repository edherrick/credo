import uuid

from sqlalchemy import TIMESTAMP, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.user import Base


class Agenda(Base):
    __tablename__ = "agendas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    metric_id: Mapped[str | None] = mapped_column(Text, ForeignKey("metrics.id"), nullable=True)
    geography_id: Mapped[str | None] = mapped_column(Text, ForeignKey("geographies.id"), nullable=True)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    target_value: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    target_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
