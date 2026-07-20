from keyboards.reply import get_reply_keyboard

# start.py
start_reply_kb = get_reply_keyboard(
                             "🌙 Сделать запись за сегодня",
                             "✏️ Изменить/добавить запись",
                             "Статистика за неделю",
                             "Статистика за месяц",
                             "⚙️ Настройки",
                             "Обратная связь",
                             placeholder="Выбери кнопку",
                             sizes=(1, 1, 2, 2)
                         )

