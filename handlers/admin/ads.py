from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InputRichMessage, Message

from database.models import Ad
from database.session import SessionLocal
from keyboards.inline.ads import (
    get_ad_inline_kb,
    get_ads_inline_kb,
    get_delete_ad_inline_kb,
)
from middlewares.admin import AdminMiddleware
from services.bot.text import TextService
from services.db.ad import AdService


ads_router = Router()

ads_router.message.middleware(AdminMiddleware())
ads_router.callback_query.middleware(AdminMiddleware())


class AdStates(StatesGroup):
    """Состояния добавления рекламной кампании."""

    campaign_name = State()
    description = State()


def build_ads(
    ads: list[Ad],
    text: TextService,
) -> InputRichMessage:
    """Формирует Rich Message со списком рекламных кампаний."""

    rows = [
        f"{ad.campaign_name} | "
        f"{ad.description or '—'}"
        for ad in ads
    ]

    return InputRichMessage(
        blocks=[
            text.heading(
                "ads-title",
                size=2,
            ),
            text.table(
                "ads-table",
                header=True,
                rows="\n".join(rows),
            ),
        ],
    )


async def render_form(
    state: FSMContext,
    text: TextService,
) -> str:
    """Формирует текст формы добавления кампании."""

    data = await state.get_data()

    return text(
        "ad-create-form",
        campaign_name=data.get("campaign_name") or "—",
        description=data.get("description") or "—",
    )


async def update_form(
    message: Message,
    state: FSMContext,
    form_text: str,
) -> None:
    """Обновляет форму добавления кампании."""

    data = await state.get_data()

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["form_message_id"],
        text=form_text,
    )


async def send_prompt(
    message: Message,
    state: FSMContext,
    prompt_text: str,
) -> None:
    """Показывает текущий вопрос."""

    data = await state.get_data()

    if prompt_id := data.get("prompt_message_id"):
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=prompt_id,
            )
        except Exception:
            pass

    prompt = await message.answer(prompt_text)

    await state.update_data(
        prompt_message_id=prompt.message_id,
    )


async def next_step(
    message: Message,
    state: FSMContext,
    next_state: State,
    form_text: str,
    prompt_text: str,
) -> None:
    """Переходит к следующему шагу."""

    await state.set_state(next_state)
    await message.delete()
    await update_form(message, state, form_text)
    await send_prompt(message, state, prompt_text)


@ads_router.message(F.text == "Реклама")
async def ads_command(
    message: Message,
    text: TextService,
) -> None:
    """Показывает список рекламных кампаний."""

    async with SessionLocal() as session:
        ad_service = AdService(session)
        ads = await ad_service.get_all()

    await message.answer_rich(
        build_ads(ads, text),
        reply_markup=get_ads_inline_kb(ads),
    )


@ads_router.callback_query(F.data == "add_ad")
async def add_ad_callback(
    callback: CallbackQuery,
    state: FSMContext,
    text: TextService,
) -> None:
    """Начинает добавление рекламной кампании."""

    await callback.answer()
    await state.set_state(AdStates.campaign_name)

    form = await callback.message.edit_text(
        await render_form(state, text),
    )

    await state.update_data(
        form_message_id=form.message_id,
    )

    await send_prompt(
        callback.message,
        state,
        text("ad-question-campaign-name"),
    )


@ads_router.message(AdStates.campaign_name)
async def process_campaign_name(
    message: Message,
    state: FSMContext,
    text: TextService,
) -> None:
    """Обрабатывает название рекламной кампании."""

    if not message.text or not message.text.strip():
        await message.delete()

        await send_prompt(
            message,
            state,
            text("ad-invalid-campaign-name"),
        )
        return

    campaign_name = message.text.strip()

    if len(campaign_name) > 64:
        await message.delete()

        await send_prompt(
            message,
            state,
            text("ad-invalid-campaign-name"),
        )
        return

    async with SessionLocal() as session:
        ad_service = AdService(session)
        existing_ad = await ad_service.get_by_campaign_name(campaign_name)

    if existing_ad:
        await message.delete()

        await send_prompt(
            message,
            state,
            text("ad-campaign-name-taken"),
        )
        return

    await state.update_data(
        campaign_name=campaign_name,
    )

    await next_step(
        message,
        state,
        AdStates.description,
        await render_form(state, text),
        text("ad-question-description"),
    )


@ads_router.message(AdStates.description)
async def process_ad_description(
    message: Message,
    state: FSMContext,
    text: TextService,
) -> None:
    """Обрабатывает описание и создает рекламную кампанию."""

    if not message.text or not message.text.strip():
        await message.delete()

        await send_prompt(
            message,
            state,
            text("ad-invalid-description"),
        )
        return

    await state.update_data(
        description=message.text.strip(),
    )

    data = await state.get_data()
    await message.delete()

    async with SessionLocal() as session:
        ad_service = AdService(session)

        ad = await ad_service.create(
            campaign_name=data["campaign_name"],
            description=data["description"],
        )

        ads = await ad_service.get_all()

    if prompt_id := data.get("prompt_message_id"):
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=prompt_id,
            )
        except Exception:
            pass

    await state.clear()

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["form_message_id"],
        text=text(
            "ad-created",
            campaign_name=ad.campaign_name,
        ),
    )

    await message.answer_rich(
        build_ads(ads, text),
        reply_markup=get_ads_inline_kb(ads),
    )


@ads_router.callback_query(F.data.regexp(r"^ad_\d+$"))
async def ad_callback(
    callback: CallbackQuery,
    text: TextService,
) -> None:
    """Показывает информацию о рекламной кампании."""

    ad_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        ad_service = AdService(session)
        ad = await ad_service.get_by_id(ad_id)

    if ad is None:
        await callback.answer(
            text("ad-not-found"),
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        text(
            "ad-info",
            campaign_name=ad.campaign_name,
            description=ad.description or "—",
        ),
        reply_markup=get_ad_inline_kb(ad),
    )

    await callback.answer()


@ads_router.callback_query(F.data.regexp(r"^delete_ad_\d+$"))
async def delete_ad_callback(
    callback: CallbackQuery,
    text: TextService,
) -> None:
    """Показывает подтверждение удаления кампании."""

    ad_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        ad_service = AdService(session)
        ad = await ad_service.get_by_id(ad_id)

    if ad is None:
        await callback.answer(
            text("ad-not-found"),
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        text(
            "ad-delete-confirm",
            campaign_name=ad.campaign_name,
        ),
        reply_markup=get_delete_ad_inline_kb(ad),
    )

    await callback.answer()


@ads_router.callback_query(F.data.regexp(r"^confirm_delete_ad_\d+$"))
async def confirm_delete_ad_callback(
    callback: CallbackQuery,
    text: TextService,
) -> None:
    """Удаляет рекламную кампанию после подтверждения."""

    ad_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        ad_service = AdService(session)

        ad = await ad_service.get_by_id(ad_id)

        if ad is None:
            await callback.answer(
                text("ad-not-found"),
                show_alert=True,
            )
            return

        await ad_service.delete(ad)
        ads = await ad_service.get_all()

    await callback.message.edit_text(
        rich_message=build_ads(ads, text),
        reply_markup=get_ads_inline_kb(ads),
    )

    await callback.answer(text("ad-deleted"))


@ads_router.callback_query(F.data.regexp(r"^back_to_ad_\d+$"))
async def back_to_ad_callback(
    callback: CallbackQuery,
    text: TextService,
) -> None:
    """Возвращает к информации о кампании."""

    ad_id = int(callback.data.split("_")[-1])

    async with SessionLocal() as session:
        ad_service = AdService(session)
        ad = await ad_service.get_by_id(ad_id)

    if ad is None:
        await callback.answer(
            text("ad-not-found"),
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        text(
            "ad-info",
            campaign_name=ad.campaign_name,
            description=ad.description or "—",
        ),
        reply_markup=get_ad_inline_kb(ad),
    )

    await callback.answer()


@ads_router.callback_query(F.data == "back_to_ads")
async def back_to_ads_callback(
    callback: CallbackQuery,
    text: TextService,
) -> None:
    """Возвращает к списку рекламных кампаний."""

    async with SessionLocal() as session:
        ad_service = AdService(session)
        ads = await ad_service.get_all()

    await callback.message.edit_text(
        rich_message=build_ads(ads, text),
        reply_markup=get_ads_inline_kb(ads),
    )

    await callback.answer()