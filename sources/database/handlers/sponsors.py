from sources.database.models import SponsorsBase

from sqlalchemy import exists, update, select, func, delete, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from datetime import datetime, timedelta
from pathlib import Path

async def addNewSponsor(session: AsyncSession, link: str, adays: int, tgid) -> float:
    try:
        stmt = select(SponsorsBase).where(SponsorsBase.link == link)
        result = await session.execute(stmt)
        sponsor = result.scalar_one_or_none()
        if sponsor is None:
            session.add(SponsorsBase(
                link=link,
                tgid=tgid,
                startDate=datetime.now(),
                finishDate=datetime.now() + timedelta(days=adays)
            ))
            await session.commit()
            return True
        else:
            return True
    except Exception as ex:
        print(f"OnAddNewSponsorError: {ex}")
        return False

async def delSponsor(session: AsyncSession, sid: int):
    try:
        stmt = delete(SponsorsBase).where(SponsorsBase.id == sid)
        result = await session.execute(stmt)
        await session.commit()
        if result.rowcount > 0:
            print(f"Спонсор с ID {sid} успешно удален")
            return True
        else:
            print(f"Спонсор с ID {sid} не найден")
            return False   
    except Exception as ex:
        print(f"OnDelSponsorError: {ex}")
        return False
    
async def dumpSponsorsInString(session: AsyncSession) -> str:
    result = await session.execute(
        select(SponsorsBase)
    )
    sponsors = result.scalars().all()
    return "\n".join(
        f"id: {s.id} "
        f"link: {s.link} "
        f"tgid: {s.tgid} "
        f"startDate: {s.startDate} "
        f"finishDate: {s.finishDate}"
        for s in sponsors
    )

async def dumpSponsorsInCSV(session: AsyncSession) -> str:
    result = await session.execute(
        select(SponsorsBase)
    )
    sponsors = result.scalars().all()
    TEMP_DIR = Path(__file__).resolve().parents[3] / "sources" / "database" / "temp"
    directory = TEMP_DIR / f"dump_sponsors_{datetime.now():%Y%m%d_%H%M%S}.csv"
    export_dir = Path(directory)
    export_dir.mkdir(parents=True, exist_ok=True)
    file_path = export_dir / f"sponsors_{datetime.now():%Y%m%d_%H%M%S}.csv"
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write("id,link,startDate,finishDate\n")
        for s in sponsors:
            f.write(
                f'"{s.id}","{s.link}","{s.startDate}","{s.finishDate}"\n'
            )
    return str(file_path.resolve())

async def getSponsorsList(session: AsyncSession) -> dict:
    try:
        stmt = select(SponsorsBase)
        result = await session.execute(stmt)
        all_op_list = result.scalars().all()
        op_links = {}
        for op in all_op_list:
            op_links[op.tgid] = op.link
        return op_links
    except Exception as ex:
        print(f"OnGetListOpLinksError: {ex}")
        return []