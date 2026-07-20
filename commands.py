from aiogram import Bot
from aiogram.types import BotCommand


# Список команд
bot_commands = [
    BotCommand(command="start", description="Начать работу с ботом"),
]

async def set_bot_commands(bot: Bot):
    """Установка листа команд"""
    try:
        await bot.set_my_commands(bot_commands)
    except Exception as e:
        print(f"Ошибка установки команд: {e}")
        