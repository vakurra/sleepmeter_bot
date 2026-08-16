from commands import bot_commands


BOT_COMMANDS = {
    f"/{command.command}"
    for command in bot_commands
}


MAIN_MENU_ACTIONS = {
    "Сделать запись за сегодня",
    "Изменить/добавить запись",
    "Статистика за 7 дней",
    "Статистика за месяц",
    "Настройки",
    "Обратная связь",
    "Пользователи",
}


GLOBAL_ACTIONS = BOT_COMMANDS | MAIN_MENU_ACTIONS