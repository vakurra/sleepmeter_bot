from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import InputRichMessage, Message, CallbackQuery
from middlewares.admin import AdminMiddleware

from keyboards.reply.admin_menu import admin_reply_kb
from services.bot.text import TextService


admin_router = Router()
admin_router.message.middleware(AdminMiddleware())
admin_router.callback_query.middleware(AdminMiddleware())


@admin_router.message(Command("admin"))
async def admin_command(message: Message, text: TextService):
    """Открывает админское меню."""

    await message.answer_rich(
        InputRichMessage(blocks=[text.heading("admin-panel-title", size=3)]),
        reply_markup=admin_reply_kb,
    )


@admin_router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, text: TextService):
    """Возвращает в админское меню."""

    await callback.answer()
    await callback.message.delete()

    await callback.message.answer_rich(
        InputRichMessage(blocks=[text.heading("admin-panel-title", size=3)]),
        reply_markup=admin_reply_kb,
    )