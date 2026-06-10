from aiogram import types, Router
from aiogram.filters import Command

from keyboards.all_reply_kbs import start_reply_kb


start_router = Router()

# Главное меню
@start_router.message(Command("start"))
async def start_command(message: types.Message):
    
    first_name = message.from_user.first_name
    await message.answer(f"С возвращением, {first_name}! Чем займемся?", reply_markup=start_reply_kb)
