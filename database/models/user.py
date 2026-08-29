from datetime import date, datetime, time
from enum import StrEnum

from sqlalchemy import BigInteger, Date, DateTime, SmallInteger, String, Time
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base


class UserRole(StrEnum):
    """Роли пользователей."""

    DEFAULT = "default"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя Telegram."""

    __tablename__ = "users"

    # В качестве первичного ключа используется Telegram User ID.
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    username: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    first_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(16),
        default=UserRole.DEFAULT,
        nullable=False,
    )

    utc_offset: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    notifications_enabled: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    reminder_time: Mapped[time | None] = mapped_column(
        Time,
        nullable=False,
    )

    # Дата последнего обработанного ежедневного напоминания.
    last_reminder_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    referred_by: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )