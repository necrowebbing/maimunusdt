from sources.database.handlers import users_db, financial, promocodes, withdraws
from sources.database.engine import session_maker

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatMemberStatus

from sources.services import tgrasshandler
from sources.states.statements import ReferrerID, CallbackStates
from sources.states.icons import icons
from sources.states.images import IMAGES
from sources.keyboards.users import MainPage
from sources.keyboards.admins import AdminKbs
from sources.utils.configmanager import AsyncConfigManager
from sources.utils import sponsors

from datetime import datetime, timedelta

import html

router = Router()

@router.callback_query(F.data == "open:main")
async def StartCommand(cb: CallbackQuery, state: FSMContext):
    if await AsyncConfigManager.get("other", "project_active"):
        data = await state.get_data()
        referrer_id = None
        if data:
            referrer_id = data.get("id")
        async with session_maker() as session:
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                user_exist = await users_db.CheckUserExistOrCreate(session, cb.from_user.username, cb.from_user.id, referrer_id)
                if user_exist['user_exist']:
                    if await users_db.IsUserNotBanned(session, cb.from_user.id):
                            if referrer_id is not None and user_exist["comment"] == "created":
                                await cb.bot.send_message(referrer_id, f"{icons.get("congratulations")} <b>Вы получили {await AsyncConfigManager.get("bonuses", "ref_bonus")}$ за приглашение нового пользователя</b>", parse_mode='HTML')
                            await cb.message.edit_text(
                                text=f"<b>{icons['hello']} Добро пожаловать, здесь вы можете заработать USDT приглашая рефералов в бота</b>",
                                parse_mode="HTML",
                                reply_markup = await MainPage.mainKb(cb.from_user.id)
                            )
                    else:
                        await cb.message.edit_text(
                        text=f"{icons.get("warning")} Доступ к боту заблокирован! Если вы считаете что произошла ошибка пожалуйста напишите в поддержку.",
                        reply_markup = await MainPage.getSupport(),
                        parse_mode="HTML"
                        )
                else:
                    await cb.message.edit_text(
                    text=f"{icons.get("warning")} Произошла ошибка! Попробуйте использовать команду вновь или обратитесь в поддержку.",
                    reply_markup = await MainPage.getSupport(),
                    parse_mode="HTML"
                    ) 
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup = await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )

# Tasks System
@router.callback_query(F.data == "open:tasks")
async def OpenTasksMenu(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"): 
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                task = await tgrasshandler.GetTask(cb.from_user.id, cb.from_user.is_premium, cb.from_user.language_code)
                taskId = task.get("offer_id")
                taskLink = task.get("link")
                task_price = await AsyncConfigManager.get("bonuses", "task_bonus")
                if task.get("status") == "not_ok":
                    type = task.get("type")
                    data = ""
                    if type == "bot":
                        data = (
                            f"{icons.get("bonus")} <b>Задание за бонус!</b>\n"
                            f"{icons.get("tasks")} <b>Категория:</b> <code>бот</code>\n"
                            f"{icons.get("tg_stars")} <b>Награда:</b> <code>{task_price} USDT</code>\n"
                        )
                    elif type == "channel":
                        data = (
                            f"{icons.get("bonus")} <b>Задание за бонус!</b>\n"
                            f"{icons.get("tasks")} <b>Категория:</b> <code>канал</code>\n"
                            f"{icons.get("tg_stars")} <b>Награда:</b> <code>{task_price} USDT</code>\n"
                        )
                    elif type == "resource":
                        data = (
                            f"{icons.get("bonus")} <b>Задание за бонус!</b>\n"
                            f"{icons.get("tasks")} <b>Категория:</b> <code>ссылка</code>\n"
                            f"{icons.get("tg_stars")} <b>Награда:</b> <code>{task_price} USDT</code>\n"
                        )
                    await cb.message.edit_text(
                        text=data,
                        parse_mode='HTML',
                        reply_markup=await MainPage.acceptTask(taskLink, taskId)
                    )
                elif task.get("status") == "ok":
                    await financial.AddMoney(session, cb.from_user.id, task_price)
                    await tgrasshandler.ResetTasks(cb.from_user.id)
                    await cb.message.edit_text(
                        text=f"<b>{icons.get("congratulations")} Задание успешно выполнено, баланс пополнен на {task_price} USDT</b>",
                        parse_mode='HTML',
                        reply_markup=await MainPage.nextTask()
                    )
                elif task.get("status") == "no_offers":
                    await cb.message.edit_text(
                        text=f"<b>{icons.get("warning")} Задания отсутствуют</b>",
                        parse_mode='HTML',
                        reply_markup=await MainPage.backToMainKb("open:main")
                    )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )   

@router.callback_query(F.data.regexp(r"^open:task:accept_"))
async def AcceptTask(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"): 
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                task_price = await AsyncConfigManager.get("bonuses", "task_bonus")
                task_id = cb.data.rsplit("_", 1)[1]
                task = await tgrasshandler.CheckTask(cb.from_user.id, task_id)
                status = task.get("status")
                is_fake = task.get("is_fake")
                if not is_fake:
                    if status == "subscribed":
                        await financial.AddMoney(session, cb.from_user.id, task_price)
                        await tgrasshandler.ResetTasks(cb.from_user.id)
                        await cb.message.edit_text(
                            text=f"<b>{icons.get("congratulations")} Задание успешно выполнено, баланс пополнен на {task_price} USDT</b>",
                            parse_mode='HTML',
                            reply_markup=await MainPage.nextTask()
                        )
                    elif status == "not_subscribed":
                        await cb.answer(
                            text=f"Задание не выполнено"
                        )
                    elif status == "user_not_found":
                        await cb.answer(
                            text=f"Ошибка: юзер не найден"
                        )
                    elif status == "offer_not_found" or status == "offer_expired": 
                        await tgrasshandler.ResetTasks(cb.from_user.id)
                        await cb.message.edit_text(
                            text=f"<b>{icons.get("clock")} Задание просрочилось или не найдено</b>",
                            parse_mode="HTML",
                            reply_markup=await MainPage.nextTask()
                        )
                else:
                    await tgrasshandler.ResetTasks(cb.from_user.id)
                    await cb.message.edit_text(
                        text=f"<b>{icons.get("warning")} Задание не засчитано</b>",
                        parse_mode="HTML",
                        reply_markup=await MainPage.nextTask()
                    )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )
# Referals
@router.callback_query(F.data == "open:refs")
async def OpenReferralsMenu(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                userdata = await users_db.GetUserData(session, cb.from_user.id)
                await cb.message.edit_text(
                    text=(
                        f"<b>{icons.get("referrals")} Партнёрская программа</b>\n\n"
                        f"<b>→ Бонус:</b> {await AsyncConfigManager.get("bonuses", "ref_bonus")} USDT\n"
                        f"<b>→ Приглашено:</b> {userdata.get('refs') if userdata.get('refs') is not None else 0}\n\n"
                        f"<b>{icons.get("link")} Ваша ссылка:</b>\n"
                        f"<code>t.me/meimunusdbot?start=ref_{cb.from_user.id}</code>\n\n"
                        f"<i>Приглашайте и получайте награду мгновенно!</i>"
                    ), 
                    parse_mode="HTML",
                    reply_markup = await MainPage.backToMainKb("open:main"),
                )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )

@router.callback_query(F.data == "open:bonus")
async def OpenAndGetBonus(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                data = await users_db.GetUserData(session, cb.from_user.id)
                if data:
                    lastDate = data.get("lastBonus")
                if lastDate is None or (datetime.now() - lastDate) >= timedelta(hours=24):        
                    await financial.AddMoney(session, cb.from_user.id, await AsyncConfigManager.get("bonuses", "daily_bonus"))
                    await users_db.SetNewBonusDate(session, cb.from_user.id, datetime.now())
                    await cb.message.edit_text(
                        text=f"{icons.get("bonus")} Ваш баланс пополнен на {await AsyncConfigManager.get("bonuses", "daily_bonus")}$!",
                        reply_markup = await MainPage.backToMainKb("open:main"),
                        parse_mode="HTML"
                    )
                else:
                    await cb.message.edit_text(
                        text=f"{icons.get("clock")}К сожалению сутки с момента прошлого получения бонуса не прошли, попробуйте позже",
                        reply_markup = await MainPage.backToMainKb("open:profile"),
                        parse_mode="HTML"
                    )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )

@router.callback_query(F.data == "open:profile")
async def OpenProfilePage(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                userdata = await users_db.GetUserData(session, cb.from_user.id)
                await cb.message.edit_text(
                    text=(
                        f"<b>{icons.get('robot')} Личный кабинет</b>\n\n"
                        f"{icons.get('profile')} <b>ID:</b> <code>{cb.from_user.id}</code>\n"
                        f"{icons.get('wallet')} <b>Баланс:</b> {round(float(userdata.get('balance', 0)), 2)} USDT\n"
                        f"{icons.get('brougthed_bucks')} <b>Выведено:</b> {round(float(userdata.get('brougth', 0)), 2)} USDT\n"
                        f"{icons.get('referrals')} <b>Рефералов:</b> {userdata.get('refs') or 0}"
                    ),
                    parse_mode="HTML",
                    reply_markup = await MainPage.getProfilePageKb(),
                )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )

@router.callback_query(F.data == "open:promo")
async def OpenPromocodePage(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                await cb.message.edit_text(
                    text=f"{icons.get("bonus")}<b>Ввод промокода</b>\n\nОтправьте промокод боту, промокоды публикуются в нашем канале",
                    parse_mode="HTML",
                    reply_markup = await MainPage.backToMainKb("open:profile")
                )
                await state.set_state(CallbackStates.promocode)
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )

@router.message(CallbackStates.promocode)
async def OnSendPromocode(msg: Message, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            isActivated = await promocodes.activatePromo(session, msg.text, msg.from_user.id)
            if isActivated:
                await msg.answer(
                    text=f"<b>{icons.get("congratulations")} Промокод успешно активирован!</b>",
                    reply_markup = await MainPage.backToMainKb("open:main"),
                    parse_mode="HTML"
                )
            else:
                await msg.answer(
                    text=f"<b>{icons.get("bad")} Промокод закончился, не существует или вы его уже активировали</b>",
                    reply_markup = await MainPage.backToMainKb("open:main"),
                    parse_mode="HTML"
                )
            await state.clear()

@router.callback_query(F.data == "open:stats")
async def OpenStatsPage(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                data = await users_db.getStateDict(session)
                broughted = await users_db.getBroughtedMoney(session)
                users_top_five_dict = await users_db.get_top_referrals_dict(session)
                users_top_five = ""
                for i, (key, value) in enumerate(users_top_five_dict.items()):
                    index = i + 1
                    users_top_five += f"{index})@{key} - {value} рефералов\n"
                await cb.message.edit_text(
                    text=(
                        f"<b>{icons.get('stats')} Статистика</b>\n\n"
                        f"{icons.get('referrals')} <b>Топ 5 рефоводов</b>\n"
                        f"{users_top_five}\n"
                        f"{icons.get('robot')} <b>Пользователей:</b> {data.get('accounts')}\n"
                        f"{icons.get("brougthed_bucks")} <b>Всего выплачено:</b> {round(float(broughted), 2)} USDT"
                    ),
                    parse_mode="HTML",
                    reply_markup = await MainPage.statsKb()
                )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )
    
@router.callback_query(F.data == "open:withdraw")
async def OpenWithdrawPage(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        if await AsyncConfigManager.get("other", "project_active"):
            if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
                await cb.message.edit_text(
                    text=f"<b>{icons.get("brougthed_bucks")} Вывод средств:</b>\nПожалуйста выберите способ вывода",
                    parse_mode="HTML",
                    reply_markup = await MainPage.getWithdrawTypesKb()
                )
            else:
                await cb.message.edit_text(
                    text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                    parse_mode="HTML",
                    reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
                )

@router.callback_query(F.data == "open:withdraw:cb")
async def OpenCryptoBotWithdrawMenu(cb: CallbackQuery, state: FSMContext):
    if await AsyncConfigManager.get("other", "project_active"):
        if await sponsors.CheckUserSubs(cb.message.bot, cb.from_user.id, state):
            await cb.message.edit_text(
                text=f"<b>{icons.get("cryptobot")} Вывод на CryptoBot:</b>\nПожалуйста укажите сумму вывода\nПримечание: вывод от {await AsyncConfigManager.get("withdraw", "min_cb_withdraw")}$",
                parse_mode="HTML",
                reply_markup = await MainPage.backToMainKb("open:withdraw")
            )
            await state.set_state(CallbackStates.withdraw_sum_cb)
        else:
            await cb.message.edit_text(
                text=f"<b>{icons.get("stop")} Перед использованием бота нужно подписаться на спонсоров проекта</b>",
                parse_mode="HTML",
                reply_markup=await sponsors.FormateKeyboard("open:main", cb.from_user.id),
            )

@router.message(CallbackStates.withdraw_sum_cb)
async def CryptoBotWithdrawReaction(msg: Message, state: FSMContext):
    if await AsyncConfigManager.get("other", "project_active"):
        try:
            async with session_maker() as session:
                allowed = True
                if not allowed:
                    await msg.answer(
                        text="Извините! Данный тип вывода сейчас отключен.",
                    )
                    return
                if msg.text == "/start":
                    await state.clear()
                    return
                wsum = float(msg.text)
                await state.clear()
                userdata = await users_db.GetUserData(session, msg.from_user.id)
                if wsum < await AsyncConfigManager.get("withdraw", "min_cb_withdraw"):
                    await msg.answer(
                        text=f"<b>{icons.get("stop")} Введеная вами сумма вывода меньше минимальной</b>",
                        parse_mode="HTML",
                        reply_markup = await MainPage.backInWithdrawKb("open:withdraw:cb")
                    )
                else:
                    if userdata["balance"] < wsum:
                        await msg.answer(
                            text=f"<b>{icons.get('stop')} Недостаточно средств на балансе</b>",
                            parse_mode="HTML",
                            reply_markup = await MainPage.backInWithdrawKb("open:withdraw:cb")
                        )
                    else:
                        await msg.answer(
                            text=f"{icons.get("brougthed_bucks")}<b> Пожалуйста проверьте</b>\n<b>{icons.get("cryptobot")} Тип вывода:</b> CryptoBot\n{icons.get("wallet")}<b>Сумма вывода:</b> {wsum}$",
                            parse_mode="HTML",
                            reply_markup = await MainPage.checkAndWithdraw("c", wsum)
                        )
        except (TypeError, ValueError):
            await msg.answer(
                text=f"<b>{icons.get("bad")} Нужно ввести число!</b>",
                parse_mode="HTML",
                reply_markup = await MainPage.backInWithdrawKb("open:withdraw:cb")
            )

@router.callback_query(F.data.contains("success_wd"))
async def ProccesingAccessedWithdraw(cb: CallbackQuery):
    try:
        if await AsyncConfigManager.get("other", "project_active"):
            async with session_maker() as session:
                r_parts = cb.data.split(":")
                wsum = float(r_parts[2])
                type = r_parts[1]
                await financial.MinusMoney(session, cb.from_user.id, wsum)
                request = await withdraws.CreateNewRequest(session, wsum, cb.from_user.id)
                if request["result"] and request["rid"] != None:
                    await cb.message.bot.send_message(
                        chat_id=await AsyncConfigManager.get("admins", "payments_requests_chat"), 
                        text=(
                            f"{icons.get("brougthed_bucks")}<b> Новая заявка на вывод</b>\n\n"
                            f"{icons.get("profile")} <b>Юзер:</b> {cb.from_user.username if cb.from_user.username else ''}({cb.from_user.id})\n"
                            f"{icons.get("clock")} <b>Дата:</b> {datetime.now()}\n"
                            f"{icons.get("wallet")} <b>Сумма:</b> {wsum}$\n"
                            f"{icons.get("code")} <b>RID:</b> {request["rid"]}\n\n"
                            f"<i>Успейте произвести вывод за 24 часа!</i>"
                        ),
                        parse_mode="HTML",
                        reply_markup = await AdminKbs.requestHandlersKb(request['rid'])
                    )
                    await cb.message.edit_text(
                        text=f"<b>Заявка успешно создана, ожидайте!</b>",
                        parse_mode="HTML",
                        reply_markup = await MainPage.backToMainKb("open:main")
                    )
    except (IndexError, ValueError):
        await cb.answer("Некорректные данные", show_alert=True)
        return
