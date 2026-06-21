from sources.database.handlers import users_db
from sources.database.engine import session_maker
from sources.utils.configmanager import AsyncConfigManager

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from sources.states.statements import ReferrerID
from sources.states.icons import icons
from sources.states.images import IMAGES
from sources.keyboards.users import MainPage

from sources.utils import sponsors

router = Router()

@router.message(CommandStart())
async def StartCommand(msg: Message, state: FSMContext):
    if await AsyncConfigManager.get("other", "project_active"):    
      refferer_id = None
      if msg.text and len(msg.text.split()) > 1:
          payload = msg.text.split()[1]
          if payload.startswith("ref_"):
            refferer_id = int(payload.replace("ref_", ""))
            if refferer_id > 0 and refferer_id != msg.from_user.id:
              print(f"Рефералка от пользователя с id: {refferer_id}")
            else:
              refferer_id = None
      await state.set_state(ReferrerID.id)
      await state.update_data(id=refferer_id)
      async with session_maker() as session:
          if await sponsors.CheckUserSubs(msg.bot, msg.from_user.id, state):
            user_exist = await users_db.CheckUserExistOrCreate(session, msg.from_user.username, msg.from_user.id, refferer_id)
            if user_exist['user_exist']:
                if await users_db.IsUserNotBanned(session, msg.from_user.id):
                    if refferer_id != None and user_exist["comment"] == "created":
                      await msg.bot.send_message(refferer_id, f"{icons.get("congratulations")} Вы получили {await AsyncConfigManager.get("bonuses", "ref_bonus")}$ за приглашение нового пользователя!", parse_mode="HTML")
                    await msg.answer(
                      text=(
                        f"{icons["hello"]} <b>Добро пожаловать, здесь вы можете заработать USDT приглашая рефералов в бота</b>"
                      ),
                      parse_mode="HTML",
                      reply_markup = await MainPage.mainKb(msg.from_user.id)
                    )
                else:
                  await msg.answer(
                    text=f"{icons.get("warning")} Доступ к боту заблокирован! Если вы считаете что произошла ошибка пожалуйста напишите в поддержку.",
                    reply_markup = await MainPage.getSupport(),
                    parse_mode="HTML"
                  )
            else:
              await msg.answer(
                text=f"{icons.get("warning")} Произошла ошибка! Попробуйте использовать команду вновь или обратитесь в поддержку.",
                reply_markup = await MainPage.getSupport(),
                parse_mode="HTML"
              ) 
          else:
            await msg.answer(
              text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
              reply_markup = await sponsors.FormateKeyboard("open:main", msg.from_user.id),
              parse_mode="HTML"
            )
