from aiogram import Bot, Dispatcher

from sources.handlers import callbacks, commands, adminshandlers
from sources.database.handlers import users_db
from sources.database.engine import initbaseandtables, DATABASE_PATH
from sources.utils.configmanager import AsyncConfigManager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import logging, asyncio, os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
bot = Bot(token="8843613001:AAExCJ4FtDJluT32fGysR_QtyfXRbNE1oos")

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

async def on_startup(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        users_db.CheckAllUsersSubsOnStatisOP,
        trigger=IntervalTrigger(hours=2),
        args=[bot],
        id="check_referral_subs",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    asyncio.create_task(users_db.CheckAllUsersSubsOnStatisOP(bot))
    scheduler.start()
    print("✅ Планировщик проверки подписок запущен")

async def main():
    await initbaseandtables()
    if os.path.exists(DATABASE_PATH):
        print(f"✅ База данных создана по пути: {DATABASE_PATH}")
    else:
        print("❌ Файл базы данных не найден, выключаемся.")
        return
    config = await AsyncConfigManager.init()
    dp = Dispatcher()
    dp.include_routers(
        callbacks.router, commands.router, adminshandlers.router
    )
    await on_startup(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__== "__main__":
    asyncio.run(main())
