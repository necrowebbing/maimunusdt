from sources.database.models import PromocodesBase
from sources.database.handlers import financial

from sqlalchemy import exists, update, select, func, delete, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

from pathlib import Path
from datetime import datetime

async def dumpFullTable(session: AsyncSession) -> str:
    try:
        stmt = select(PromocodesBase)
        result = await session.execute(stmt)
        all_promocodes_list = result.scalars().all()
        data = ""
        for promocode in all_promocodes_list:
            data += f"ID: {promocode.id} Promocode: {promocode.promocode} ActivatesLimit: {promocode.maxActivates} Activated: {promocode.activated} Prize: {promocode.prize}"
        return data
    except Exception as ex:
        ...

async def findPromocodeById(session: AsyncSession, id: int) -> dict:
    try:
        stmt = select(PromocodesBase).where(PromocodesBase.id == id)
        result = await session.execute(stmt)
        promocode = result.scalar_one_or_none()
        if promocode is None:
            return {"result": None}
        promocode_dict = {
            "result": True,
            'id': promocode.id,
            'promocode': promocode.promocode,
            'prize': promocode.prize,
            'activates': f'{promocode.activated}/{promocode.maxActivates}'
        }
        return promocode_dict
    except Exception as ex:
        print(f"OnFIndPromocodeByIdError: {ex}")
        return {"result": None}

async def activatePromo(session: AsyncSession, promo: str, user_id: int):
    try:
        query = select(PromocodesBase).where(PromocodesBase.promocode == promo)
        result = await session.execute(query)
        promocode = result.scalar_one_or_none()
        if promocode is None:
            return False
        if promocode.activated_by and user_id in promocode.activated_by:
            return False
        if promocode.maxActivates > promocode.activated:
            await financial.AddMoney(session, user_id, promocode.prize)
            promocode.activated += 1
            if promocode.activated_by is None:
                promocode.activated_by = []
            promocode.activated_by.append(user_id)
            await session.commit()
            return True
        else:
            await delPromo(session, promocode.id)
            return False                
    except Exception as ex:
        print(f"ONPROMOCODEACTIVATIONERROR: {ex}")
        return False

async def getActivePromocodes(session: AsyncSession) -> list:
    query = select(PromocodesBase)
    result = await session.execute(query)
    promocodes = result.scalars().all()
    promocodes_list = []
    for promocode in promocodes:
        promocode_dict = {
            "id": promocode.id,
            "promocode": promocode.promocode,
            "maxActivates": promocode.maxActivates,
            "activated": promocode.activated,
            "prize": promocode.prize
        }
        promocodes_list.append(promocode_dict)        
    return promocodes_list

async def createPromo(session: AsyncSession, promocode, activates, prize):
    promo = PromocodesBase(
            promocode=promocode,
            maxActivates=activates,
            activated=0,
            prize=prize
    )
    session.add(promo)
    await session.commit()    

async def delPromo(session: AsyncSession, promocode_id) -> bool:
    stmt = delete(PromocodesBase).where(PromocodesBase.id == promocode_id)
    result = await session.execute(stmt)
    await session.commit()
    if result.rowcount > 0:
        print(f"Промокод с ID {promocode_id} успешно удален")
        return True
    else:
        print(f"Промокод с ID {promocode_id} не найден")
        return False    
    
