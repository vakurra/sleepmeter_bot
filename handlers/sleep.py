from datetime import datetime, timedelta, timezone

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from database.session import SessionLocal
from keyboards.inline.sleep_record import (
    get_cancel_record_kb,
    get_sleep_end_kb,
    get_sleep_rating_kb,
    get_sleep_start_kb
)
from keyboards.reply.start_menu import start_reply_kb
from services.bot import sleep_record_flow
from services.bot.text import TextService
from services.db.sleep import SleepService
from services.db.user import UserService
from utils.parsers import parse_time, parse_date


sleep_router = Router()


class SleepRecordStates(StatesGroup):
    choose_date = State()
    sleep_start = State()
    sleep_start_manual = State()
    sleep_end = State()
    sleep_end_manual = State()
    sleep_rating = State()


@sleep_router.message(F.text == "Изменить/добавить запись")
async def start_change_record(message: types.Message, state: FSMContext, text: TextService):
    """Начало изменения записи."""

    await state.set_state(SleepRecordStates.choose_date)

    await message.answer(text("sleep-record-date"), reply_markup=get_cancel_record_kb())


@sleep_router.message(SleepRecordStates.choose_date)
async def choose_record_date(message: types.Message, state: FSMContext, text: TextService):
    try:
        record_date = parse_date(message.text)
    except ValueError:
        await message.answer(text("sleep-record-date-invalid"))
        return

    async with SessionLocal() as session:
        sleep_service = SleepService(session)

        record = await sleep_service.get_by_date(
            user_id=message.from_user.id,
            record_date=record_date,
        )

        if record:
            await message.answer(
                text("sleep-record-edit-for", record_date=f"{record_date:%d.%m.%Y}"),
                reply_markup=ReplyKeyboardRemove(),
            )

            edit_mode = True

        else:
            await message.answer(
                text("sleep-record-create-for", record_date=f"{record_date:%d.%m.%Y}"),
                reply_markup=ReplyKeyboardRemove(),
            )

            edit_mode = False

        await state.update_data(record_date=record_date, edit_mode=edit_mode)
        await state.set_state(SleepRecordStates.sleep_start)

        question = await message.answer(text("sleep-record-start"), reply_markup=get_sleep_start_kb())

        await state.update_data(wizard_message_id=question.message_id)


@sleep_router.message(F.text == "Сделать запись за сегодня")
async def add_sleep_record(message: types.Message, state: FSMContext, text: TextService):
    """Начало добавления записи."""

    async with SessionLocal() as session:
        user_service = UserService(session)
        sleep_service = SleepService(session)
        user = await user_service.get_by_id(message.from_user.id)
        local_datetime = datetime.now(timezone.utc) + timedelta(hours=user.utc_offset)
        record_date = local_datetime.date()
        record = await sleep_service.get_by_date(user_id=user.id, record_date=record_date)

    if record:
        await message.answer(text("sleep-record-exist"), reply_markup=start_reply_kb)
        return
    
    await state.set_state(SleepRecordStates.sleep_start)
    await state.update_data(record_date=record_date, edit_mode=False)

    await message.answer(
        text("sleep-record-for", record_date=f"{record_date:%d.%m.%Y}"),
        reply_markup=ReplyKeyboardRemove(),
    )

    question = await message.answer(text("sleep-record-start"), reply_markup=get_sleep_start_kb())


@sleep_router.callback_query(
    SleepRecordStates.sleep_start,
    F.data.startswith("sleep_start_")
    & (F.data != "sleep_start_manual"),
)
async def select_sleep_start(call: CallbackQuery, state: FSMContext):
    """Выбор времени отхода ко сну."""

    await state.update_data(sleep_start=parse_time(call.data.removeprefix("sleep_start_")))
    await sleep_record_flow.ask_sleep_end(call, state, SleepRecordStates.sleep_end)


@sleep_router.callback_query(SleepRecordStates.sleep_start, F.data == "sleep_start_manual")
async def manual_sleep_start(call: CallbackQuery, state: FSMContext, text: TextService):
    """Переход к ручному вводу времени."""

    await state.set_state(SleepRecordStates.sleep_start_manual)
    await call.message.edit_text(text("sleep-record-start-manual"))
    await call.answer()


@sleep_router.message(SleepRecordStates.sleep_start_manual)
async def input_sleep_start(message: types.Message, state: FSMContext, text: TextService):
    """Ручной ввод времени отхода ко сну."""

    try:
        sleep_start = parse_time(message.text)

    except ValueError:
        await message.answer(text("sleep-record-time-invalid"))
        return

    await state.update_data(sleep_start=sleep_start,)

    await sleep_record_flow.ask_sleep_end(
        message,
        state,
        SleepRecordStates.sleep_end,
    )


@sleep_router.callback_query(
    SleepRecordStates.sleep_end,
    F.data.startswith("sleep_end_")
    & (F.data != "sleep_end_manual"),
)
async def select_sleep_end(call: CallbackQuery, state: FSMContext):
    """Выбор времени пробуждения."""

    await state.update_data(sleep_end=parse_time(call.data.removeprefix("sleep_end_")))
    await sleep_record_flow.ask_sleep_rating(call, state, SleepRecordStates.sleep_rating)


@sleep_router.callback_query(SleepRecordStates.sleep_end, F.data == "sleep_end_manual")
async def manual_sleep_end(call: CallbackQuery, state: FSMContext, text: TextService):
    """Переход к ручному вводу времени пробуждения."""

    await state.set_state(SleepRecordStates.sleep_end_manual)
    await call.message.edit_text(text("sleep-record-wakeup-manual"))
    await call.answer()


@sleep_router.message(SleepRecordStates.sleep_end_manual)
async def input_sleep_end(message: types.Message, state: FSMContext, text: TextService):
    """Ручной ввод времени пробуждения."""

    try:
        sleep_end = parse_time(message.text)

    except ValueError:
        await message.answer(text("sleep-record-time-invalid"))
        return

    await state.update_data(sleep_end=sleep_end)
    await sleep_record_flow.ask_sleep_rating(
        message,
        state,
        SleepRecordStates.sleep_rating,
    )


@sleep_router.callback_query(SleepRecordStates.sleep_end, F.data == "sleep_back")
async def back_to_sleep_start(call: CallbackQuery, state: FSMContext, text: TextService):
    """Возврат к выбору времени отхода ко сну."""

    await state.set_state(SleepRecordStates.sleep_start)
    await call.message.edit_text(text("sleep-record-start"), reply_markup=get_sleep_start_kb())
    await call.answer()


@sleep_router.callback_query(SleepRecordStates.sleep_rating, F.data == "sleep_rating_back")
async def back_to_sleep_end(call: CallbackQuery, state: FSMContext, text: TextService):
    """Возвращает к выбору времени пробуждения."""

    await state.set_state(SleepRecordStates.sleep_end)
    await call.message.edit_text(text("sleep-record-wakeup"), reply_markup=get_sleep_end_kb())
    await call.answer()


@sleep_router.callback_query(SleepRecordStates.sleep_rating, F.data.startswith("sleep_rating_"))
async def select_sleep_rating(call: CallbackQuery, state: FSMContext):
    """Выбор оценки сна."""

    await state.update_data(sleep_rating=int(call.data.removeprefix("sleep_rating_")))
    await sleep_record_flow.finish_sleep_record(call, state)


@sleep_router.callback_query(F.data == "sleep_cancel")
async def cancel_sleep_record(call: CallbackQuery, state: FSMContext, text: TextService):
    """Отменяет добавление записи."""

    await state.clear()
    await call.message.edit_text(text("sleep-record-cancel"))
    await call.message.answer(text("start-whats-next"), reply_markup=start_reply_kb)
    await call.answer()