# import asyncio
# from datetime import datetime, timedelta, timezone

# from aiogram import Bot, Dispatcher
# from aiogram.exceptions import TelegramForbiddenError

# from handlers.sleep import SleepRecordStates
# from keyboards.all_inline_kbs import get_sleep_start_kb
# from database.session import SessionLocal
# from services.sleep_service import SleepService
# from services.user_service import UserService


# async def process_reminders(bot: Bot, dp: Dispatcher):
#     """Проверяет и обрабатывает ежедневные напоминания."""

#     current_utc = datetime.now(timezone.utc)

#     async with SessionLocal() as session:

#         user_service = UserService(session)
#         sleep_service = SleepService(session)

#         users = await user_service.get_reminder_candidates()

#         for user in users:
#             try:
#                 local_datetime = current_utc + timedelta(hours=user.utc_offset)
#                 local_date = local_datetime.date()
#                 local_time = local_datetime.time().replace(tzinfo=None)

#                 if user.last_reminder_date == local_date:
#                     continue

#                 if local_time < user.reminder_time:
#                     continue

#                 record = await sleep_service.get_by_date(
#                     user.id,
#                     local_date,
#                 )

#                 if record:
#                     user_service.update_last_reminder_date(
#                         user,
#                         local_date,
#                     )
#                     continue

#                 state = dp.fsm.get_context(
#                     bot=bot,
#                     chat_id=user.id,
#                     user_id=user.id,
#                 )

#                 await state.set_state(SleepRecordStates.sleep_start)
#                 await state.update_data(
#                     record_date=local_date,
#                     edit_mode=False,
#                 )

#                 await bot.send_message(
#                     chat_id=user.id,
#                     text=(
#                         "🌙 Доброе утро!\n\n"
#                         f"Давайте сделаем запись за {local_date.strftime('%d.%m.%Y')}\n"
#                         "Во сколько вы легли спать?"
#                     ),
#                     reply_markup=get_sleep_start_kb(),
#                 )

#                 user_service.update_last_reminder_date(
#                     user,
#                     local_date,
#                 )

#             except TelegramForbiddenError:
#                 user_service.update_notifications_enabled(
#                     user,
#                     False,
#                 )

#         await session.commit()


# async def reminder_scheduler(bot: Bot, dp: Dispatcher):
#     """Запускает постоянную проверку ежедневных напоминаний."""

#     while True:
#         try:
#             await process_reminders(bot, dp)

#         except Exception as e:
#             print(f"Ошибка scheduler: {type(e).__name__}: {e}")

#         now = datetime.now(timezone.utc)
#         seconds_to_next_minute = 60 - now.second - now.microsecond / 1_000_000

#         await asyncio.sleep(seconds_to_next_minute)