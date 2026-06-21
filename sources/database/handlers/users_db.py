from sources.database.models import UserBase
from sources.keyboards.users import MainPage
from sources.states.icons import icons
from sources.utils.configmanager import AsyncConfigManager
from sources.database.engine import session_maker
from sources.database.handlers import sponsors, financial

from aiogram.enums import ChatMemberStatus
from aiogram.types import Message
from aiogram import Bot

from sqlalchemy import exists, update, select, func, delete, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from pathlib import Path
from datetime import datetime
from typing import Dict

async def HowManyRefsInSystem(session: AsyncSession) -> int:
    try:
        accountsQuery = select(func.count()).select_from(UserBase).where(UserBase.referrerId.is_not(None))
        accountsResult = await session.execute(accountsQuery)
        return accountsResult.scalar() or 0
    except Exception as ex:
        print(f"ONHowManyRefsInSystemError: {ex}")
        return 0
    
async def HowManyUsersInSystem(session: AsyncSession) -> int:
    try:
        accountsQuery = select(func.count()).select_from(UserBase)
        accountsResult = await session.execute(accountsQuery)
        return accountsResult.scalar() or 0
    except Exception as ex:
        print(f"ONHowManyUsersInSystemError: {ex}")
        return 0

async def dumpUsersIdInList(session: AsyncSession) -> list:
    try:
        stmt = select(UserBase)
        result = await session.execute(stmt)
        all_users_list = result.scalars().all()
        users_ids = []
        for user in all_users_list:
            users_ids.append(user.tgId)
        return users_ids
    except Exception as ex:
        print(f"OnDumpUsersIdError: {ex}")
        return []

async def CheckUserExistOrCreate(session: AsyncSession, username: str, user_id, referrer) -> Dict:
    try:
        stmt = select(UserBase).where(UserBase.tgId == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            session.add(UserBase(
                username=username,
                tgId=user_id,
                balance=0,
                referrerId=referrer,
                referrals=0,
                lastBonus=None,
                isBanned=False,
                brought=0
            ))
            await session.commit()
            try:
                if referrer and referrer != user_id:
                    stmt = select(UserBase).where(UserBase.tgId == referrer)
                    res = await session.execute(stmt)
                    ref_user = res.scalar_one_or_none()
                    if ref_user is not None:
                        stmt = update(UserBase).where(UserBase.tgId == referrer).values(referrals=UserBase.referrals + 1, balance=UserBase.balance + await AsyncConfigManager.get("bonuses", "ref_bonus"))
                        await session.execute(stmt)
                        await session.commit()
            except Exception:
                await session.rollback()
            print(f"Создание юзера: Юзер с id: {user_id} только что был добавлен в бд, он имеет реферала с id: {referrer}")
            return {
                "user_exist": True,
                "comment": "created",
                "error": None
            }
        return {
            "user_exist": True,
            "comment": "is exist",
            "error": None
        }
    except Exception as e:
        await session.rollback()
        print(f'Создание юзера: {e}')
        return {
            "user_exist": False,
            "comment": None,
            "error": f"{e}"
        }
    
async def IsUserNotBanned(session: AsyncSession, tgid: int) -> bool:
        try:
            stmt = select(UserBase).where(UserBase.tgId == tgid)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            if user is None:
                return True
            if user.isBanned:
                return False
            else:
                return True
        except Exception as ex:
            print(f"OnUserBanCheckError: {ex}")
            return False

async def GetUserData(session: AsyncSession, tgid: int) -> dict:
    try:
        stmt = select(UserBase).where(UserBase.tgId == tgid)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return {"result": None}
        user_dict = {
            'result': True,
            'username': user.username,
            'tgId': user.tgId,
            'balance': user.balance,
            'refId': user.referrerId,
            'refs': user.referrals,
            'lastBonus': user.lastBonus,
            'brought': user.brought,
            'banStatus': user.isBanned
        }  
        return user_dict
    except Exception as e:
        print(f'GetUserDataByTgIdError: {e}')
        return {"result": None}

async def SetNewBonusDate(session: AsyncSession, tgid, value) -> bool:
    try:
        stmt = update(UserBase).where(UserBase.tgId == tgid).values(lastBonus=value)
        await session.execute(stmt)
        await session.commit()
        return True
    except Exception as ex:
        print("OnSetNewBonusEx:" + ex)
        return False

async def getBroughtedMoney(session: AsyncSession) -> int:
    query = select(func.sum(UserBase.brought))
    result = await session.execute(query)
    utotal_sum = result.scalar()
    data = utotal_sum if utotal_sum is not None else 0
    return data

async def get_top_referrals_dict(session: AsyncSession, limit: int = 5) -> Dict[int, int]:
    try:
        query = (
            select(UserBase.username, UserBase.referrals)
            .order_by(desc(UserBase.referrals))
            .limit(limit)
        )
        result = await session.execute(query)
        referrals_dict = {row.username: row.referrals for row in result.all()}            
        return referrals_dict
        
    except Exception as e:
        print(f"Ошибка при получении топ рефералов: {e}")
        raise



async def getStateDict(session: AsyncSession) -> dict:
    data = {
        "accounts": 0,
        "usersMoney": 0, 
        "moneyForWithdraw": 0,
        "botCapital": 0
    }
    
    #wMquery = select(func.sum(WithdrawBase.money)).where(WithdrawBase.isPaid.is_(False))
    #wMresult = await session.execute(wMquery)
    #wtotal_sum = wMresult.scalar()
    #data["moneyForWithdraw"] = wtotal_sum or 0
        
    bot_capital = None
    data["botCapital"] = bot_capital if bot_capital is not None else 0
        
    return data

async def BanUnBanUser(session: AsyncSession, tgid: int, bot: Message.bot) -> bool:
    try:
        stmt = select(UserBase).where(UserBase.tgId == tgid)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            return False
        oldStatus = user.isBanned
        stmt = update(UserBase).where(UserBase.tgId == tgid).values(isBanned = not oldStatus)
        await session.execute(stmt)
        await session.commit()
        if oldStatus:
            await bot.send_message(
                chat_id=f"{tgid}",
                text=f"<b>{icons.get("congratulations")} Вы были разблокированы.</b>",
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=f"{tgid}",
                text=f"<b>{icons.get("warning")} Вы были заблокированы, если вы считаете что произошла ошибка обратитесь в поддержку.</b>",
                reply_markup = await MainPage.getSupport(),
                parse_mode="HTML"
            )
        return True
    except Exception as ex:
        print(f"OnUserBanUnbanError: {ex}")
        return False
    
async def CheckSubsOnStatisSponsors(session: AsyncSession, telegram_id: int, bot: Bot) -> bool:
    sponsors_dict = await sponsors.getSponsorsList(session)
    for key, value in sponsors_dict.items():
        member = await bot.get_chat_member(
            chat_id=int(key),
            user_id=int(telegram_id)
        )
        if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            print(f"❌ Пользователь {telegram_id} НЕ подписан на канал {key} ({value})")
            return False
        print(f"✅ Пользователь {telegram_id} подписан на канал {key} ({value})")
    print(f"🎉 Пользователь {telegram_id} подписан на ВСЕ статические спонсорские каналы")   
    return True

async def GiveWarnUserByID(session: AsyncSession, telegram_id: int, bot: Bot):
    stmt = select(UserBase).where(UserBase.tgId == telegram_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    warnPrice = await AsyncConfigManager.get("sponsors", "unsubed_warn_price")
    await financial.MinusMoney(session, telegram_id, warnPrice)
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"{icons.get("warning")} <b>Вы отписались со спонсора и получили штраф в размере {warnPrice} USDT</b>"
        ),
        parse_mode='HTML'
    )
    if user.referrerId != None:
        warnPrice = warnPrice - (warnPrice / 100 * 40)
        await financial.MinusMoney(session, user.referrerId, warnPrice)
        await bot.send_message(
            chat_id=user.referrerId,
            text=(
                f"{icons.get("warning")} <b>Ваш реферал отписался со спонсора, вы получили штраф в размере {warnPrice} USDT</b>"
            ),
            parse_mode='HTML'
        )        
    user.alreadyWarned = True  
    await session.commit()

async def CheckAllUsersSubsOnStatisOP(bot: Bot):
    try:
        async with session_maker() as session:
            stmt = select(UserBase)
            result = await session.execute(stmt)
            all_users_list = result.scalars().all()
            warnPrice = await AsyncConfigManager.get("sponsors", "unsubed_warn_price")
            totalUnSubed = 0
            
            print(f"🔔Начинается проверка подписок рефералов")
            await bot.send_message(
                chat_id=-1003837278734,
                text=f"<b>Начинается проверка подписок рефералов</b>\n<b>Штраф за отписку:</b> <code>{warnPrice} USDT</code>\n<b>Всего юзеров:</b> <code>{len(all_users_list)}</code>",
                parse_mode="HTML"
            )
            errors = 0
            for user in all_users_list:
                try:
                    if await CheckSubsOnStatisSponsors(session, user.tgId, bot):
                        continue
                    else:
                        if user.alreadyWarned: 
                            totalUnSubed = totalUnSubed + 1
                            continue
                        await GiveWarnUserByID(session, user.tgId, bot)
                except Exception as ex:
                    print(f"Ошибка при проверке юзера: {user.tgId}, ex: {ex}")
                    errors = errors + 1
            await bot.send_message(
                chat_id=-1003837278734,
                text=f"<b>Проверка подписок рефералов закончилась</b>\n<b>Штрафов начислено:</b> <code>{totalUnSubed}</code>\n<b>Штрафов на сумму:</b> <code>{totalUnSubed * warnPrice} USDT</code>\n<b>Ошибок:</b> <code>{errors}</code>",
                parse_mode="HTML"
            )
            totalUnSubed = None
    except Exception as ex:
        print(f"Ошибка в CheckAllUsersSubsOnStatisOP: {ex}")