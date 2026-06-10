import asyncio
from aiogram import types, Router, F
from aiogram.filters import Command
from utils.kwork_monitor import monitor, monitoring_loop
from keyboards.all_reply_kbs import get_kwork_monitoring_kb

kwork_monitoring_router = Router()

# Управление мониторингом
@kwork_monitoring_router.message(Command("kwork_monitoring"))
@kwork_monitoring_router.message(F.text == "🔗 Мониторинг Kwork")
async def kwork_monitoring_command(message: types.Message):

    await message.answer(
        f"Kwork мониторинг\n\n"
        f"Статус: {'Работает' if monitor.enabled else 'Бездействует'}\n"
        f"Категория: {monitor.category}\n"
        f"ID в памяти: {len(monitor.seen_ids)}",
        reply_markup=get_kwork_monitoring_kb(monitor.enabled)
    )


# Переключение работы парсера
@kwork_monitoring_router.message(F.text.in_(["🟢 Включить", "🔴 Выключить"]))
async def toggle_monitoring(message: types.Message):
    
    monitor.enabled = not monitor.enabled
    if monitor.enabled:
        if not monitor.initialized:
            monitor.initialize()

        if monitor.task is None:
            monitor.task = asyncio.create_task(
                monitoring_loop(message.bot, message.chat.id)
            )
    
    await message.answer(
        f"Kwork мониторинг\n\n"
        f"Статус: {'Работает' if monitor.enabled else 'Бездействует'}\n"
        f"Категория: {monitor.category}\n"
        f"ID в памяти: {len(monitor.seen_ids)}",
        reply_markup=get_kwork_monitoring_kb(monitor.enabled)
    )  