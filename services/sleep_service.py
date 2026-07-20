from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import SleepRecord


class SleepService:
    """Сервис для работы с записями сна."""

    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_by_date(
        self,
        user_id: int,
        record_date: date,
    ) -> SleepRecord | None:
        """Возвращает запись пользователя за указанную дату."""

        return await self.session.scalar(
            select(SleepRecord).where(
                SleepRecord.user_id == user_id,
                SleepRecord.record_date == record_date,
            )
        )


    async def save(
        self,
        user_id: int,
        record_date: date,
        sleep_start: time,
        sleep_end: time,
        sleep_duration: int,
        sleep_rating: int,
    ) -> bool:
        """Создает новую запись или обновляет существующую."""

        record = await self.get_by_date(
            user_id,
            record_date,
        )

        created = record is None

        if created:
            record = SleepRecord(
                user_id=user_id,
                record_date=record_date,
            )
            self.session.add(record)

        record.sleep_start = sleep_start
        record.sleep_end = sleep_end
        record.sleep_duration = sleep_duration
        record.sleep_rating = sleep_rating

        await self.session.commit()

        return created


    async def get_by_period(
        self,
        user_id: int,
        date_from: date,
        date_to: date,
    ) -> list[SleepRecord]:
        """Возвращает записи пользователя за указанный период."""

        result = await self.session.execute(
            select(SleepRecord)
            .where(
                SleepRecord.user_id == user_id,
                SleepRecord.record_date >= date_from,
                SleepRecord.record_date <= date_to,
            )
            .order_by(SleepRecord.record_date)
        )

        return list(result.scalars().all())