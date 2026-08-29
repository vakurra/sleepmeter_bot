from database.models import Ad
from keyboards.builders import get_inline_keyboard
from constants import emoji


def get_ads_inline_kb(ads: list[Ad]):
    """Создает inline-клавиатуру со списком рекламных кампаний."""

    buttons = {
        "Назад": ("back_to_admin", "danger", emoji.BACK),
        "Добавить": ("add_ad", "success", emoji.ADD),
    }

    buttons.update(
        {
            ad.campaign_name: (f"ad_{ad.id}", None, None)
            for ad in ads
        }
    )

    return get_inline_keyboard(
        buttons=buttons,
        sizes=(2, 1,),
    )


def get_ad_inline_kb(ad: Ad):

    return get_inline_keyboard(
        buttons={
            "Удалить": (f"delete_ad_{ad.id}", "danger", emoji.DELETE),
            "Назад": ("back_to_ads", None, emoji.BACK),
        },
        sizes=(1,),
    )


def get_delete_ad_inline_kb(ad: Ad):

    return get_inline_keyboard(
        buttons={
            "Подтвердить": (
                f"confirm_delete_ad_{ad.id}",
                "danger",
                emoji.DELETE,
            ),
            "Назад": (
                f"back_to_ad_{ad.id}",
                None,
                emoji.BACK,
            ),
        },
        sizes=(1,),
    )