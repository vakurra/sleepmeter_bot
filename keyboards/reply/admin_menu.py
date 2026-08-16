from constants import emoji
from keyboards.builders import get_reply_keyboard


admin_reply_kb = get_reply_keyboard(
    buttons={
        "Пользователи": (None, emoji.USERS),
    },
    sizes=(1,),
)