from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from typing import Union

from sources.utils.configmanager import AsyncConfigManager
from sources.database.handlers import sponsors as ophandler
from sources.database.engine import session_maker
from sources.services import piarflowhandler


# =========================
# STATIC SPONSORS
# =========================

async def GetStaticSponsors() -> dict:
    """
    Берём статических спонсоров из конфига + базы
    """
    async with session_maker() as session:
        db_sponsors = await ophandler.getSponsorsList(session)
        return db_sponsors


# =========================
# DYNAMIC SPONSORS
# =========================

async def GetDynamicSponsors(telegram_id: int, chat_id: int):
    """
    Всегда возвращает чистую структуру:
    {
        "status": "all_ok" | "existed" | "error",
        "links": [...]
    }
    """

    pf_result = await piarflowhandler.GetSponsors(telegram_id, chat_id)

    if not pf_result:
        return {"status": "error", "links": []}

    status = pf_result[0]

    if status == "error":
        return {"status": "error", "links": []}

    if status == "all_ok":
        return {"status": "all_ok", "links": []}

    links = pf_result[1:]
    return {"status": "existed", "links": links}


# =========================
# KEYBOARD BUILDER
# =========================

async def FormateKeyboard(callback: str, telegram_id: int) -> InlineKeyboardMarkup:
    """
    Собирает клаву из:
    - static sponsors
    - dynamic sponsors
    """
    print(f"[Formate Keyboard] GetStaticSponsors()")
    sponsors = await GetStaticSponsors()
    print(f"[Formate Keyboard] GetDynamicSponsors()")
    dynamic = await GetDynamicSponsors(telegram_id, telegram_id)
    links = dynamic["links"]
    print(F"links: {links}")

    print(f"[Formate Keyboard] for in links")
    for i, link in enumerate(links):
        sponsors[f"dynamic_{i}"] = link

    buttons = []
    print(f"[Formate Keyboard] for in buttons")

    for i, link in enumerate(sponsors.values()):
        if not link:
            continue
        print(f"[Formate Keyboard] Adding button for link: {link} | i: {i} | i+1: {i + 1}")
        buttons.append([
            InlineKeyboardButton(
                text=f"Спонсор №{i + 1}",
                url=link
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="Проверить",
            callback_data=callback
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# SUBS CHECK
# =========================

async def CheckUserSubs(bot: Union[Bot, Message.bot], telegram_id: int, state: FSMContext = None) -> bool:
    """
    Проверка подписок (статические + динамические)
    """

    sponsors = await GetStaticSponsors()

    # 1) STATIC CHECK
    for channel_id, _ in sponsors.items():
        if not channel_id:
            continue

        try:
            member = await bot.get_chat_member(
                chat_id=int(channel_id),
                user_id=int(telegram_id)
            )

            if member.status not in (
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR
            ):
                return False

        except Exception as e:
            print(f"[STATIC CHECK ERROR] {channel_id}: {e}")
            return False

    # 2) DYNAMIC CHECK
    dynamic = await GetDynamicSponsors(telegram_id, telegram_id)

    if dynamic["status"] == "error":
        return False

    if dynamic["status"] == "all_ok":
        return True

    links = dynamic["links"]

    if not links:
        return True
    print(f"[CheckUserSubs] Dynamic links to check: {links}")
    pf_result = await piarflowhandler.CheckSubsOnSponsors(
        telegram_id,
        links
    )
    print(f"[CheckUserSubs] Result from piarflowhandler: {pf_result}")
    if not pf_result or pf_result[0] != "all_ok":
        return False

    return True
