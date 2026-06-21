from sources.database.models import UserBase, WithdrawsBase

from sqlalchemy import exists, update, select, func, delete, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict

import datetime

async def CreateNewRequest(session: AsyncSession, withdraw_sum: int, telegram_id: int) -> dict:
    try:
        request = WithdrawsBase(
            tgId=telegram_id,
            isAccepted=None,
            requestDate=datetime.datetime.now(),
            verificationDate=None,
            sum=withdraw_sum
        )
        session.add(request)
        await session.commit()
        await session.refresh(request)
        if request.id is not None:
            return {
                "result": True,
                "rid": request.id
            }
        else:
            return {
                "result": True,
                "rid": None
            }
    except Exception as ex:
        print(f"OnCreateNewWIthdrawRequestError: {ex}")
        await session.rollback()
        return {
            "result": False
        }
    
async def ChangeRequestStatus(session: AsyncSession, request_id: int, acceptStatus: bool):
    try:
        stmt = update(WithdrawsBase).where(WithdrawsBase.id == request_id).values(verificationDate=datetime.datetime.now(), isAccepted=acceptStatus)
        await session.execute(stmt)
        await session.commit()
        return True
    except Exception as ex:
        print(f"OnChangeRequestStatus: {ex}")
        await session.rollback()
        return False

async def GetRequestData(session: AsyncSession, requestId: int):
        try:
            stmt = select(WithdrawsBase).where(WithdrawsBase.id == requestId)
            result = await session.execute(stmt)
            request = result.scalars().one_or_none()
            if request is None:
                print(f"Запись WithdrawsBase с id={requestId} не найдена")
                return None 
            return {
                "tgid": request.tgId,
                "sum": request.sum
            }
        except SQLAlchemyError as e:
            print(f"Ошибка БД при получении записи {requestId}: {str(e)}")    
        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")
            raise

async def GetTotalRequests(session: AsyncSession) -> int:
    try:
        requestsQuery = select(func.count()).select_from(WithdrawsBase).where(WithdrawsBase.isAccepted.is_not(None))
        requestsResult = await session.execute(requestsQuery)
        return requestsResult.scalar() or 0
    except Exception as ex:
        print(f"ONGetTotalRequestsError: {ex}")
        return 0
    
async def GetTotalRequestsOnSleep(session: AsyncSession) -> int:
    try:
        requestsQuery = select(func.count()).select_from(WithdrawsBase).where(WithdrawsBase.isAccepted.is_(None))
        requestsResult = await session.execute(requestsQuery)
        return requestsResult.scalar() or 0
    except Exception as ex:
        print(f"ONGetTotalRequestsOnSleepError: {ex}")
        return 0