import uuid

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import TIMESTAMP, ForeignKey, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    profile: Mapped["UserProfile"] = relationship(
        back_populates="user", uselist=False, lazy="selectin"
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="profile")
