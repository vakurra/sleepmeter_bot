from keyboards.reply import get_reply_keyboard

# start.py
start_reply_kb = get_reply_keyboard(
                             "заглушка",
                             "заглушка",
                             "заглушка на будущее",
                             "🔗 Мониторинг Kwork",
                             placeholder="Выбери кнопку",
                             sizes=(2, 1, 1)
                         )

# kwork_monitoring.py
def get_kwork_monitoring_kb(enabled: bool):

    on_text = "✅🟢 Включен" if enabled else "🟢 Включить"
    off_text = "✅🔴 Выключен" if not enabled else "🔴 Выключить"

    return get_reply_keyboard(
        on_text,
        off_text,
        placeholder="Переключатель работы",
        sizes=(2,)
    )