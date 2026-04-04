from geoalchemy2 import Geometry
from sqlalchemy import TIMESTAMP, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from models.user import Base


class Geography(Base):
    __tablename__ = "geographies"

    id: Mapped[str] = mapped_column(Text, primary_key=True)  # FIPS code
    name: Mapped[str] = mapped_column(Text, nullable=False)
    state_fips: Mapped[str] = mapped_column(Text, nullable=False)
    geo_type: Mapped[str] = mapped_column(Text, nullable=False, default="county")
    boundary: Mapped[bytes | None] = mapped_column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
