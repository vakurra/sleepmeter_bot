from commands import bot_commands


BOT_COMMANDS = {
    f"/{command.command}"
    for command in bot_commands
}


MAIN_MENU_ACTIONS = {
    "🌙 Сделать запись за сегодня",
    "✏️ Изменить/добавить запись",
    "Статистика за неделю",
    "Статистика за месяц",
    "⚙️ Настройки",
    "Обратная связь",
}


GLOBAL_ACTIONS = BOT_COMMANDS | MAIN_MENU_ACTIONS