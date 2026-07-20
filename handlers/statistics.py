from datetime import datetime, timedelta, timezone

from aiogram import F, Router, types
from aiogram.methods import SendRichMessage
from aiogram.types import InputRichMessage

from database.session import SessionLocal
from services.sleep_service import SleepService
from services.user_service import UserService


statistics_router = Router()


async def send_statistics(message: types.Message, days: int):
    """Формирует и отправляет статистику сна за указанный период."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        sleep_service = SleepService(session)

        user = await user_service.get_by_id(message.from_user.id)

        local_datetime = datetime.now(timezone.utc) + timedelta(hours=user.utc_offset)
        date_to = local_datetime.date()
        date_from = date_to - timedelta(days=days - 1)

        records = await sleep_service.get_by_period(
            user_id=user.id,
            date_from=date_from,
            date_to=date_to,
        )

    if not records:
        await message.answer(
            f"📊 За последние {days} дней пока нет данных о сне."
        )
        return

    total_duration = sum(record.sleep_duration for record in records)
    average_duration = total_duration // len(records)
    average_hours, average_minutes = divmod(average_duration, 60)
    average_rating = round(sum(record.sleep_rating for record in records) / len(records), 2)

    table_rows = []

    for record in records:
        hours, minutes = divmod(record.sleep_duration, 60)

        duration_text = (
            f"{hours} ч"
            if minutes == 0
            else f"{hours} ч {minutes} мин"
        )

        rating = "⭐" * record.sleep_rating

        table_rows.append(
            f"| {record.record_date:%d.%m} "
            f"| {record.sleep_start:%H:%M} "
            f"| {record.sleep_end:%H:%M} "
            f"| {duration_text} "
            f"| {rating} |"
        )

    rich_markdown = (
        f"## 📊 Статистика за последние {days} дней\n\n"
        f"**Заполнено дней:** {len(records)} из {days}\n\n"
        f"**Средняя продолжительность сна:** "
        f"{average_hours} ч {average_minutes} мин\n\n"
        f"**Средняя оценка:** {average_rating}\n\n"
        "| Дата | Отбой | Подъем | Сон | Качество |\n"
        "|:----:|:-----:|:------:|----:|:--------:|\n"
        + "\n".join(table_rows)
    )

    await message.bot(
        SendRichMessage(
            chat_id=message.chat.id,
            rich_message=InputRichMessage(
                markdown=rich_markdown,
            ),
        )
    )


@statistics_router.message(F.text == "Статистика за неделю")
async def get_week_statistics(message: types.Message):
    """Отправляет статистику сна за последние 7 дней."""

    await send_statistics(message, 7)


@statistics_router.message(F.text == "Статистика за месяц")
async def get_month_statistics(message: types.Message): 
    """Отправляет статистику сна за последние 30 дней."""

    await send_statistics(message, 30)


# TODO: свернуть таблицу месячной статистики в RichBlockDetails.(пока не разобрался в документации)