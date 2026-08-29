import asyncio
import logging
from datetime import date, datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramForbiddenError
from sqlalchemy import select

from database.session import SessionLocal
from database.models import User
from handlers.sleep import SleepRecordStates
from keyboards.inline.sleep_record import get_sleep_start_kb
from services.bot.text import TextService
from services.db.sleep import SleepService
from services.db.user import UserService


logger = logging.getLogger(__name__)
text = TextService()


async def _release_reminder_claim(
    user_id: int,
    reminder_date: date,
    previous_reminder_date: date | None,
) -> None:
    """Снимает отметку, если отправка напоминания не состоялась."""

    try:
        async with SessionLocal() as session:
            user = await session.scalar(
                select(User).where(
                    User.id == user_id,
                    User.last_reminder_date == reminder_date,
                )
            )

            if user:
                user.last_reminder_date = previous_reminder_date
                await session.commit()

    except Exception:
        # Восстановить попытку лучше, чем оставить пользователя без
        # напоминания, но ошибка здесь не должна остановить scheduler.
        logger.exception(
            "Не удалось снять отметку напоминания для пользователя %s",
            user_id,
        )


async def _disable_notifications(user_id: int) -> None:
    """Отключает уведомления после блокировки бота пользователем."""

    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.id == user_id))

        if user:
            user.notifications_enabled = False
            await session.commit()


async def process_reminders(bot: Bot, dp: Dispatcher):
    """Проверяет и обрабатывает ежедневные напоминания."""

    current_utc = datetime.now(timezone.utc)

    # Получаем актуальный список пользователей.
    async with SessionLocal() as session:
        user_service = UserService(session)
        users = await user_service.get_reminder_candidates()

    for user in users:
        reminder_claimed = False
        state = None
        previous_reminder_date = None

        try:
            state = dp.fsm.get_context(
                bot=bot,
                chat_id=user.id,
                user_id=user.id,
            )

            # Активный сценарий не прерываем. Дату здесь не отмечаем: после
            # завершения сценария следующая проверка сможет принять решение
            # по актуальному состоянию пользователя.
            if await state.get_state() is not None:
                continue

            # Повторно читаем пользователя и блокируем его строку. Список
            # candidates был загружен раньше, поэтому его объект мог устареть.
            # Обновление даты до запроса в Telegram делает операцию
            # идемпотентной при повторном запуске scheduler.
            async with SessionLocal() as session:
                db_user = await session.scalar(
                    select(User)
                    .where(User.id == user.id)
                    .with_for_update()
                )

                if not db_user or not db_user.notifications_enabled:
                    continue

                local_datetime = current_utc + timedelta(
                    hours=db_user.utc_offset,
                )
                local_date = local_datetime.date()
                local_time = local_datetime.time().replace(tzinfo=None)

                if db_user.last_reminder_date == local_date:
                    continue

                if local_time < db_user.reminder_time:
                    continue

                sleep_service = SleepService(session)

                record = await sleep_service.get_by_date(
                    db_user.id,
                    local_date,
                )

                if record:
                    db_user.last_reminder_date = local_date
                    await session.commit()
                    continue

                previous_reminder_date = db_user.last_reminder_date
                db_user.last_reminder_date = local_date
                await session.commit()
                reminder_claimed = True

            # Повторная проверка закрывает небольшое окно между первым
            # чтением FSM и фиксацией claim в БД.
            if await state.get_state() is not None:
                await _release_reminder_claim(
                    user.id,
                    local_date,
                    previous_reminder_date,
                )
                reminder_claimed = False
                continue

            # Сначала создаём контекст записи, чтобы входящий callback не
            # попал в старое состояние между отправкой и set_state().
            await state.set_state(SleepRecordStates.sleep_start)
            await state.update_data(
                record_date=local_date,
                edit_mode=False,
            )

            # Telegram вызывается вне транзакции БД. Дата уже занята выше,
            # поэтому параллельный проход не отправит второе сообщение.
            await bot.send_message(
                chat_id=user.id,
                text=text(
                    "sleep-record-start-notification",
                    record_date=local_date.strftime("%d.%m.%Y"),
                ),
                reply_markup=get_sleep_start_kb(),
            )

        except TelegramForbiddenError:
            logger.warning(
                "Пользователь %s заблокировал бота. "
                "Отключаем уведомления.",
                user.id,
            )

            try:
                await _disable_notifications(user.id)
            except Exception:
                logger.exception(
                    "Не удалось отключить уведомления для пользователя %s",
                    user.id,
                )

            if state is not None and reminder_claimed:
                try:
                    await state.clear()
                except Exception:
                    logger.exception(
                        "Не удалось очистить FSM пользователя %s",
                        user.id,
                    )

        except Exception:
            logger.exception(
                "Ошибка обработки напоминания для пользователя %s",
                user.id,
            )

            if reminder_claimed:
                if state is not None:
                    try:
                        await state.clear()
                    except Exception:
                        logger.exception(
                            "Не удалось очистить FSM пользователя %s",
                            user.id,
                        )

                await _release_reminder_claim(
                    user.id,
                    local_date,
                    previous_reminder_date,
                )


async def reminder_scheduler(bot: Bot, dp: Dispatcher):
    """Запускает постоянную проверку ежедневных напоминаний."""

    while True:
        try:
            await process_reminders(bot, dp)

        except asyncio.CancelledError:
            raise

        except Exception:
            logger.exception("Критическая ошибка scheduler")

        now = datetime.now(timezone.utc)
        seconds_to_next_minute = (
            60 - now.second - now.microsecond / 1_000_000
        )

        await asyncio.sleep(seconds_to_next_minute)
