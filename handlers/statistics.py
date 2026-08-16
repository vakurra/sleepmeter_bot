from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.methods import SendRichMessage
from aiogram.types import Message, InputRichMessage

from database.session import SessionLocal
from services.bot.text import TextService
from services.db.sleep import SleepService
from services.db.user import UserService


statistics_router = Router()


async def send_statistics(message: Message, days: int, text: TextService):
    """Формирует и отправляет статистику сна за указанный период."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        sleep_service = SleepService(session)

        user = await user_service.get_by_id(message.from_user.id)

        local_datetime = (
            datetime.now(timezone.utc) + timedelta(hours=user.utc_offset)
        )

        date_to = local_datetime.date()
        date_from = date_to - timedelta(days=days - 1)

        records = await sleep_service.get_by_period(
            user_id=user.id,
            date_from=date_from,
            date_to=date_to,
        )

    if not records:
        await message.answer(text("statistics-empty", days=days))
        return

    total_duration = sum(
        record.sleep_duration
        for record in records
    )

    average_duration = total_duration // len(records)
    average_hours, average_minutes = divmod(average_duration, 60)

    average_duration_text = (
        f"{average_hours} ч"
        if average_minutes == 0
        else f"{average_hours} ч {average_minutes} мин"
    )

    average_rating = round(
        sum(record.sleep_rating for record in records)
        / len(records),
        2,
    )

    rows = []

    for record in records:
        hours, minutes = divmod(record.sleep_duration, 60)

        duration_text = (
            f"{hours} ч"
            if minutes == 0
            else f"{hours} ч {minutes} мин"
        )

        rating = "⭐" * record.sleep_rating

        rows.append(
            f"{record.record_date:%d.%m} | "
            f"{record.sleep_start:%H:%M} | "
            f"{record.sleep_end:%H:%M} | "
            f"{duration_text} | "
            f"{rating}"
        )

    rich_message = InputRichMessage(
        blocks=[
            text.heading("statistics-title", days=days),
            text.paragraph(
                "statistics-filled-days",
                filled_days=len(records),
                days=days,
            ),
            text.paragraph(
                "statistics-average-duration",
                average_duration=average_duration_text,
            ),
            text.paragraph(
                "statistics-average-rating",
                average_rating=average_rating,
            ),
            text.table(
                "statistics-table",
                striped=True,
                rows="\n".join(rows),
            ),
        ],
    )

    await message.bot(
        SendRichMessage(
            chat_id=message.chat.id,
            rich_message=rich_message,
        )
    )


@statistics_router.message(F.text == "Статистика за 7 дней")
async def get_week_statistics(message: Message, text: TextService):
    """Отправляет статистику сна за последние 7 дней."""

    await send_statistics(message, 7, text)


@statistics_router.message(F.text == "Статистика за месяц")
async def get_month_statistics(message: Message, text: TextService):
    """Отправляет статистику сна за последние 30 дней."""

    await send_statistics(message, 30, text)