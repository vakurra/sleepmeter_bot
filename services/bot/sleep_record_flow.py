from datetime import date, datetime, timedelta

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputRichMessage

from database.session import SessionLocal
from keyboards.inline.sleep_record import get_sleep_end_kb, get_sleep_rating_kb
from keyboards.reply.start_menu import start_reply_kb
from services.db.sleep import SleepService
from services.bot.text import TextService


async def ask_sleep_end(
    target: types.Message | CallbackQuery,
    state: FSMContext,
    sleep_end_state,
):
    """Переходит к выбору времени пробуждения."""
    
    text = TextService()
    await state.set_state(sleep_end_state)
    question = text("sleep-record-wakeup")

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(question, reply_markup=get_sleep_end_kb())
        await target.answer()
    else:
        await target.answer(question, reply_markup=get_sleep_end_kb())


async def ask_sleep_rating(
    target: types.Message | CallbackQuery,
    state: FSMContext,
    sleep_rating_state,
):
    """Переходит к оценке сна."""

    text = TextService()
    await state.set_state(sleep_rating_state)
    question = text("sleep-record-rating")

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(question, reply_markup=get_sleep_rating_kb())
        await target.answer()
    else:
        await target.answer(question, reply_markup=get_sleep_rating_kb())


async def finish_sleep_record(target: types.Message | CallbackQuery, state: FSMContext):
    """Сохраняет запись о сне."""

    text = TextService()
    data = await state.get_data()

    async with SessionLocal() as session:
        sleep_service = SleepService(session)

        record_date = data["record_date"]
        sleep_start = data["sleep_start"]
        sleep_end = data["sleep_end"]

        sleep_start_dt = datetime.combine(date.min, sleep_start)
        sleep_end_dt = datetime.combine(date.min, sleep_end)

        if sleep_end_dt <= sleep_start_dt:
            sleep_end_dt += timedelta(days=1)

        sleep_duration = int(
            (sleep_end_dt - sleep_start_dt).total_seconds() // 60
        )

        await sleep_service.save(
            user_id=target.from_user.id,
            record_date=record_date,
            sleep_start=sleep_start,
            sleep_end=sleep_end,
            sleep_duration=sleep_duration,
            sleep_rating=data["sleep_rating"],
        )

    await state.clear()

    hours, minutes = divmod(sleep_duration, 60)

    sleep_duration_text = (
        f"{hours} ч"
        if minutes == 0
        else f"{hours} ч {minutes} мин"
    )

    verb = ("изменена" if data["edit_mode"] else "добавлена")

    success_text = text("sleep-record-edit-success", verb=verb)

    table = InputRichMessage(
        blocks = [
            text.table(
                "sleep-record-edit-table",
                header=False,
                striped=False,
                sleep_start=f"{sleep_start:%H:%M}",
                sleep_end=f"{sleep_end:%H:%M}",
                sleep_duration_text=sleep_duration_text,
                sleep_rating=data["sleep_rating"],
            )
        ]
    )

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(success_text)
        await target.message.answer_rich(table, reply_markup=start_reply_kb)
        await target.answer()

    else:
        await target.answer(success_text)
        await target.answer_rich(table, reply_markup=start_reply_kb)