from datetime import date, datetime, timedelta

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.session import SessionLocal
from keyboards.all_inline_kbs import get_sleep_end_kb, get_sleep_rating_kb
from keyboards.all_reply_kbs import start_reply_kb
from services.sleep_service import SleepService


async def ask_sleep_end(
    target: types.Message | CallbackQuery,
    state: FSMContext,
    sleep_end_state,
):
    """Переходит к выбору времени пробуждения."""

    await state.set_state(sleep_end_state)

    text = "Во сколько проснулись?"

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=get_sleep_end_kb())
        await target.answer()
    else:
        await target.answer(text, reply_markup=get_sleep_end_kb())


async def ask_sleep_rating(
    target: types.Message | CallbackQuery,
    state: FSMContext,
    sleep_rating_state,
):
    """Переходит к оценке сна."""

    await state.set_state(sleep_rating_state)
    text = "Оцените качество сна:"

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=get_sleep_rating_kb())
        await target.answer()
    else:
        await target.answer(text, reply_markup=get_sleep_rating_kb())


async def finish_sleep_record(
    target: types.Message | CallbackQuery,
    state: FSMContext,
):
    """Сохраняет запись о сне."""

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

        sleep_duration = int((sleep_end_dt - sleep_start_dt).total_seconds() // 60)

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

    sleep_duration_text = (f"{hours} ч" if minutes == 0 else f"{hours} ч {minutes} мин")
    verb = "изменена" if data["edit_mode"] else "добавлена"
    success_text = (
        f"✅ Запись успешно {verb}!\n\n"
        f"🌙 Отбой: {sleep_start:%H:%M}\n"
        f"🌅 Подъем: {sleep_end:%H:%M}\n"
        f"😴 Сон: {sleep_duration_text}\n"
        f"⭐ Оценка: {data['sleep_rating']}/5"
    )

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(success_text)
        await target.message.answer("Что хотите сделать дальше?", reply_markup=start_reply_kb)
        await target.answer()
    else:
        await target.answer(success_text)
        await target.answer("Что хотите сделать дальше?", reply_markup=start_reply_kb,)