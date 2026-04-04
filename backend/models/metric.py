from sqlalchemy import TIMESTAMP, BigInteger, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.user import Base


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    provider_id: Mapped[str] = mapped_column(Text, nullable=False, default="platform")
    data_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )


class MetricValue(Base):
    __tablename__ = "metric_values"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    metric_id: Mapped[str] = mapped_column(Text, ForeignKey("metrics.id"), nullable=False)
    geography_id: Mapped[str] = mapped_column(Text, ForeignKey("geographies.id"), nullable=False)
    value: Mapped[float] = mapped_column(Numeric, nullable=False)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ingested_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
