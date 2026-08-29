from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    SmallInteger,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database.base import Base


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
    record_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    sleep_start: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    sleep_end: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    sleep_duration: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    sleep_rating: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )