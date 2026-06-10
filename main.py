import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import get_routers
from commands import set_bot_commands
from utils.is_admin import IsAdmin


#Cоздание бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.message.filter(IsAdmin())
dp.callback_query.filter(IsAdmin())

# Подключение роутеров команд
for router in get_routers():
    dp.include_router(router)

async def main():
    try:
        await set_bot_commands(bot)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Критическая ошибка! Бот остановлен: {e}")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())