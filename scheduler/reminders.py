import asyncio
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError

from database.session import SessionLocal
from handlers.sleep import SleepRecordStates
from keyboards.inline.sleep_record import get_sleep_start_kb
from services.db.sleep import SleepService
from services.db.user import UserService
from services.bot.text import TextService


text = TextService()


async def process_reminders(bot: Bot, dp: Dispatcher):
    """Проверяет и обрабатывает ежедневные напоминания."""

    current_utc = datetime.now(timezone.utc)

    async with SessionLocal() as session:

        user_service = UserService(session)
        sleep_service = SleepService(session)

        users = await user_service.get_reminder_candidates()

        for user in users:
            try:
                local_datetime = current_utc + timedelta(hours=user.utc_offset)
                local_date = local_datetime.date()
                local_time = local_datetime.time().replace(tzinfo=None)

                if user.last_reminder_date == local_date:
                    continue

                if local_time < user.reminder_time:
                    continue

                record = await sleep_service.get_by_date(
                    user.id,
                    local_date,
                )

                if record:
                    user_service.update_last_reminder_date(
                        user,
                        local_date,
                    )
                    continue

                state = dp.fsm.get_context(
                    bot=bot,
                    chat_id=user.id,
                    user_id=user.id,
                )

                if await state.get_state() is not None:
                    user_service.update_last_reminder_date(
                        user,
                        local_date,
                    )
                    continue

                await bot.send_message(
                    chat_id=user.id,
                    text=text(
                        "sleep-record-start-notification",
                        record_date=local_date.strftime("%d.%m.%Y"),
                    ),
                    reply_markup=get_sleep_start_kb(),
                )

                await state.set_state(SleepRecordStates.sleep_start)
                await state.update_data(
                    record_date=local_date,
                    edit_mode=False,
                )

                user_service.update_last_reminder_date(
                    user,
                    local_date,
                )

            except TelegramForbiddenError:
                user_service.update_notifications_enabled(
                    user,
                    False,
                )

            except Exception as error:
                await session.rollback()
                print(
                    "Ошибка напоминания для "
                    f"{user.id}: {type(error).__name__}: {error}"
                )

        await session.commit()


async def reminder_scheduler(bot: Bot, dp: Dispatcher):
    """Запускает постоянную проверку ежедневных напоминаний."""

    while True:
        try:
            await process_reminders(bot, dp)

        except asyncio.CancelledError:
            raise

        except Exception as error:
            print(
                f"Ошибка scheduler: {type(error).__name__}: {error}"
            )

        now = datetime.now(timezone.utc)
        seconds_to_next_minute = (
            60 - now.second - now.microsecond / 1_000_000
        )

        await asyncio.sleep(seconds_to_next_minute)
