from sources.database.models import UserBase, WithdrawsBase

from sqlalchemy import exists, update, select, func, delete, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

async def getTotalWithdrawal(session: AsyncSession) -> float:
    query = select(func.sum(UserBase.brought))
    result = await session.execute(query)
    utotal_sum = result.scalar()
    withdrawal = utotal_sum if utotal_sum is not None else 0
    return withdrawal

async def getTotalMoneyForWithdraw(session: AsyncSession) -> float:
    wMquery = select(func.sum(WithdrawsBase.sum)).where(WithdrawsBase.isAccepted.is_(None))
    wMresult = await session.execute(wMquery)
    wtotal_sum = wMresult.scalar()
    return wtotal_sum or 0

async def getTotalBalances(session: AsyncSession) -> float:
    query = select(func.sum(UserBase.balance))
    result = await session.execute(query)
    utotal_sum = result.scalar()
    balances = utotal_sum if utotal_sum is not None else 0
    return balances

async def AddMoney(session: AsyncSession, tgid, value):
    try:
        stmt = update(UserBase).where(UserBase.tgId == tgid).values(balance=UserBase.balance + value)
        await session.execute(stmt)
        await session.commit()
    except:
        pass

async def MinusMoney(session: AsyncSession, tgid, value):
    try:
        stmt = update(UserBase).where(UserBase.tgId == tgid).values(balance=UserBase.balance - value)
        await session.execute(stmt)
        await session.commit()
    except:
        pass
