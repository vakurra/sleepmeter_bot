from aiogram import F, Router, types, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import LabeledPrice, CallbackQuery

from database.session import SessionLocal
from keyboards.all_reply_kbs import start_reply_kb
from keyboards.all_inline_kbs import get_feedback_kb, get_support_options
from services.user_service import UserService

from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
feedback_router = Router()


class FeedbackStates(StatesGroup):
    message = State()


@feedback_router.message(F.text == "Обратная связь")
async def start_feedback(message: types.Message, state: FSMContext):
    """Начинает отправку обратной связи."""

    await state.set_state(FeedbackStates.message)

    await message.answer(
        "💬 Напишите замечание, предложение "
        "или расскажите о проблеме.\n\n"
        "Следующее сообщение будет отправлено разработчику.",
        reply_markup=get_feedback_kb(),
    )


@feedback_router.callback_query(FeedbackStates.message, F.data == "support_dev")
async def choose_support(call: CallbackQuery, state: FSMContext,):

    await state.clear()
    await call.message.edit_text(
    "❤️ Спасибо за желание поддержать проект!\n\nВыберите сумму:",
    reply_markup=get_support_options()
)
    await call.answer()


@feedback_router.callback_query(F.data == "support_back")
async def support_back(call: CallbackQuery, state: FSMContext):

    await state.set_state(FeedbackStates.message)    
    await call.message.edit_text(
        "💬 Напишите замечание, предложение "
        "или расскажите о проблеме.\n\n"
        "Следующее сообщение будет отправлено разработчику.",
        reply_markup=get_feedback_kb())


@feedback_router.callback_query(F.data.startswith("support_amount:"))
async def support_dev(call: CallbackQuery):
    
    amount = int(call.data.split(":")[1])
    await call.answer()
    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title="Поддержать разработчика",
        description="Это действие не открывает никаких дополнительных функций.",
        payload=f"support_{amount}",
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Поддержка проекта",
                amount=amount,
            )
        ],
    )


@feedback_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@feedback_router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    await message.answer(
        "❤️ Спасибо за поддержку!\n\n"
        "Она помогает развивать проект и делать его лучше.",
        message_effect_id="5159385139981059251",
    )


@feedback_router.message(FeedbackStates.message)
async def process_feedback(
    message: types.Message,
    state: FSMContext,
):
    """Отправляет обратную связь администраторам."""

    if not message.text:
        await message.answer(
            "Я принимаю только текстовые сообщения.\n"
            "Попробуйте отправить текст."
        )

        return

    async with SessionLocal() as session:
        user_service = UserService(session)

        admins = await user_service.get_admins()


    feedback_text = (
        "💬 <b>Новая обратная связь</b>\n\n"
        f"<b>От:</b> {html.quote(message.from_user.full_name)}\n"
        f"<b>Username:</b> "
        f"@{html.quote(message.from_user.username or 'нет')}\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>\n\n"
        f"<b>Сообщение:</b>\n"
        f"{html.quote(message.text)}"
    )

    for admin in admins:
        await message.bot.send_message(
            chat_id=admin.id,
            text=feedback_text,
        )

    await state.clear()

    await message.answer(
        "✅ Спасибо! Сообщение отправлено разработчику.",
        reply_markup=start_reply_kb,
    )


@feedback_router.callback_query(FeedbackStates.message, F.data == "feedback_cancel")
async def cancel_feedback(call: types.CallbackQuery, state: FSMContext):
    """Отменяет отправку обратной связи."""

    await state.clear()
    await call.message.edit_text("✅ Отправка отменена.")
    await call.answer()


@feedback_router.message(Command("refund"))
async def cmd_refund(message: types.Message, bot: Bot, command: CommandObject):

    t_id = command.args

    if t_id is None:
        await message.answer("Не указан ID транзакции")
        return

    # пытаемся сделать рефанд
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=t_id
        )
        await message.answer("Возврат успешно выполнен!")

    except TelegramBadRequest as e:
        err_text = "Неверный ID транзакции"

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            err_text = "Возврат уже выполнен"

        await message.answer(err_text)
        return