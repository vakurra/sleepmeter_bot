import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from middlewares.global_action import GlobalActionMiddleware
from middlewares.throttling import ThrottlingMiddleware
from middlewares.localization import LocalizationMiddleware

from commands import set_bot_commands
from config import BOT_TOKEN
from handlers import get_routers
# from scheduler.reminders import reminder_scheduler
from database.session import engine
from services.bot.text import TextService


text_service = TextService()

# Создание бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
dp.message.outer_middleware(GlobalActionMiddleware())
dp.message.outer_middleware(ThrottlingMiddleware())
dp.message.outer_middleware(LocalizationMiddleware(text_service))
dp.callback_query.middleware(LocalizationMiddleware(text_service))



# Подключение роутеров команд
for router in get_routers():
    dp.include_router(router)


async def main():
    # scheduler_task = asyncio.create_task(reminder_scheduler(bot, dp))

    try:
        await set_bot_commands(bot)
        await dp.start_polling(bot)

    except Exception as e:
        print(f"Критическая ошибка! Бот остановлен: {e}")

    finally:
        # scheduler_task.cancel()

        # try:
        #     await scheduler_task
        # except asyncio.CancelledError:
        #     pass
        
        await engine.dispose()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())