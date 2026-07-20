from datetime import date, datetime, time
from enum import StrEnum

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    BigInteger,
    Time,
    UniqueConstraint,
    CheckConstraint,
    String,
)
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


class SleepRecord(Base):
    """Запись о сне пользователя."""

    __tablename__ = "sleep_records"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "record_date",
            name="uq_user_record_date",
        ),
        CheckConstraint(
            "sleep_rating BETWEEN 1 AND 5",
            name="ck_sleep_rating",
        ),
    )

    # Уникальный идентификатор записи.
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Пользователь, которому принадлежит запись.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Дата, к которой относится сон.
    # Например, если пользователь спал ночью со 2 на 3 июля,
    # запись относится к 3 июля.
    record_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    # Время, когда пользователь лег спать.
    sleep_start: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    sleep_end: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    # Продолжительность сна в минутах.
    sleep_duration: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    sleep_rating: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    # Время создания записи.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )