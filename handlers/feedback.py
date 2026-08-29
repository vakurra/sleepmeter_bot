from aiogram import F, Router, Bot, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery

from database.session import SessionLocal
from keyboards.inline.feedback import (
    get_feedback_kb,
    get_support_options,
    get_feedback_answer_kb,
    get_feedback_answer_cancel_kb,
)
from keyboards.reply.start_menu import start_reply_kb
from middlewares.admin import AdminMiddleware
from services.bot.text import TextService
from services.db.user import UserService


feedback_router = Router()
feedback_admin_router = Router()

feedback_admin_router.message.middleware(AdminMiddleware())
feedback_admin_router.callback_query.middleware(AdminMiddleware())

class FeedbackStates(StatesGroup):
    message = State()

class FeedbackReplyStates(StatesGroup):
    message = State()


@feedback_router.message(F.text == "Обратная связь")
async def start_feedback(message: Message, state: FSMContext, text: TextService):
    """Начинает отправку обратной связи."""

    await state.set_state(FeedbackStates.message)
    await message.answer(text("feedback-start"), reply_markup=get_feedback_kb())


@feedback_router.callback_query(FeedbackStates.message, F.data == "support_dev")
async def choose_support(call: CallbackQuery, state: FSMContext, text: TextService):
    """Открывает выбор суммы поддержки."""

    await state.clear()
    await call.message.edit_text(text("feedback-support"), reply_markup=get_support_options())
    await call.answer()


@feedback_router.callback_query(F.data == "support_back")
async def support_back(call: CallbackQuery, state: FSMContext, text: TextService):
    """Возвращает пользователя к отправке обратной связи."""

    await state.set_state(FeedbackStates.message)
    await call.message.edit_text(text("feedback-start"), reply_markup=get_feedback_kb())
    await call.answer()


@feedback_router.callback_query(F.data.startswith("support_amount:"))
async def support_dev(call: CallbackQuery, text: TextService):
    """Создает счет на поддержку проекта."""

    amount = int(call.data.split(":")[1])
    await call.answer()

    await call.bot.send_invoice(
        chat_id=call.from_user.id,
        title=text("support-payment-title"),
        description=text("support-payment-description"),
        payload=f"support_{amount}",
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(
                label=text("support-payment-label"),
                amount=amount,
            )
        ],
    )


@feedback_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    
    await pre_checkout_query.answer(ok=True)


@feedback_router.message(F.successful_payment)
async def successful_payment(message: Message, text: TextService):
    
    await message.answer(
        text("support-payment-success"),
        message_effect_id="5159385139981059251",
    )


@feedback_router.message(FeedbackStates.message)
async def process_feedback(message: Message, state: FSMContext, text: TextService):
    """Отправляет обратную связь администраторам."""

    if not message.text:
        await message.answer(text("feedback-not-text"))
        return

    async with SessionLocal() as session:
        user_service = UserService(session)
        admins = await user_service.get_admins()

    feedback_text = text(
        "feedback-new",
        full_name=html.quote(message.from_user.full_name),
        username=html.quote(message.from_user.username or "нет"),
        user_id=message.from_user.id,
        message=html.quote(message.text),
    )

    for admin in admins:
        await message.bot.send_message(
            chat_id=admin.id,
            text=feedback_text,
            reply_markup=get_feedback_answer_kb(message.from_user.id),
        )

    await state.clear()
    await message.answer(text("feedback-sent"), reply_markup=start_reply_kb)


@feedback_router.callback_query(FeedbackStates.message, F.data == "feedback_cancel")
async def cancel_feedback(call: CallbackQuery, state: FSMContext, text: TextService):
    """Отменяет отправку обратной связи."""

    await state.clear()
    await call.message.edit_text(text("feedback-cancelled"))
    await call.answer()


@feedback_router.message(Command("refund"))
async def cmd_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
    text: TextService,
):
    """Возвращает звезды по ID транзакции."""

    transaction_id = command.args

    if transaction_id is None:
        await message.answer(text("refund-missing-id"))
        return

    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id,
        )

        await message.answer(text("refund-success"))

    except TelegramBadRequest as e:
        if "CHARGE_ALREADY_REFUNDED" in e.message:
            await message.answer(text("refund-already-refunded"))
        else:
            await message.answer(text("refund-invalid-id"))


@feedback_router.message(Command("paysupport"))
async def cmd_paysupport(message: Message, text: TextService):
    """Информация о возврате звезд."""

    await message.answer(text("paysupport"))


@feedback_admin_router.callback_query(F.data.startswith("feedback_reply:"))
async def start_feedback_reply(call: CallbackQuery, state: FSMContext, text: TextService):
    """Начинает подготовку ответа пользователю."""

    user_id = int(call.data.split(":", 1)[1])

    await state.set_state(FeedbackReplyStates.message)
    await state.update_data(
        feedback_user_id=user_id,
        feedback_message=call.message.text,
    )

    await call.message.answer(
        text("feedback-reply-start"),
        reply_markup=get_feedback_answer_cancel_kb(),
    )

    await call.answer()


@feedback_admin_router.message(FeedbackReplyStates.message)
async def send_feedback_reply(message: Message, state: FSMContext, text: TextService):
    """Отправляет ответ администратора пользователю."""

    if not message.text:
        await message.answer(text("feedback-not-text"))
        return

    data = await state.get_data()
    user_id = data["feedback_user_id"]

    reply_text = (
        f"<b>{text('feedback-developer-answer-title')}</b>\n\n"
        f"{html.quote(message.text)}"
    )

    try:
        await message.bot.send_message(chat_id=user_id, text=reply_text)
    except TelegramBadRequest:
        await message.answer(text("feedback-reply-error"))
        return

    await state.clear()
    await message.answer(text("feedback-reply-sent"))


@feedback_admin_router.callback_query(FeedbackReplyStates.message, F.data == "feedback_reply_cancel")
async def cancel_feedback_reply(call: CallbackQuery, state: FSMContext, text: TextService):
    """Отменяет ответ на обратную связь."""

    await state.clear()
    await call.message.edit_text(text("feedback-reply-cancelled"))
    await call.answer()
    