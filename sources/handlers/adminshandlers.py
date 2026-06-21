from sources.database.handlers import users_db, financial, promocodes, withdraws, sponsors as ophandler
from sources.database.engine import session_maker, DATABASE_PATH
from sources.services import pastebinhandler, tempshhandler, cryptobot

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatMemberStatus

from sources.states.statements import ReferrerID, CallbackStates, AdminStates
from sources.states.icons import icons
from sources.states.images import IMAGES
from sources.keyboards.users import MainPage
from sources.keyboards.admins import AdminKbs
from sources.utils.configmanager import AsyncConfigManager
from sources.utils import sponsors
from sources.utils import filters

from sources.services import cryptobot

from datetime import datetime, timedelta

import html, os

router = Router()

# Main Menu

@router.message(Command("/admin"), filters.IsAdmin())
async def OpenMainAdminMenuByCMD(msg: Message):
    await msg.answer(
        text=(
            f"<b>{icons.get("code")} Админ-панель</b>\n"
            f"<b>{icons.get('active' if await AsyncConfigManager.get('other', 'project_active') else 'nonactive')} Статус:</b> {'Online' if await AsyncConfigManager.get('other', 'project_active') else 'Offline'}\n"
            f"{icons.get("clock")} Старт проекта: {await AsyncConfigManager.get("other", "project_start_date")}\n"
            f"{icons.get("clock")} Сегодня: {datetime.today().strftime("%d.%m.%Y")}"
        ),
        parse_mode="HTML",
        reply_markup = await AdminKbs.mainPanelKb()
    )
@router.callback_query(F.data == "admin:main", filters.IsAdmin())
async def OpenMainAdminMenu(cb: CallbackQuery):
    await cb.message.edit_text(
        text=(
            f"<b>{icons.get("code")} Админ-панель</b>\n"
            f"<b>{icons.get('active' if await AsyncConfigManager.get('other', 'project_active') else 'nonactive')} Статус:</b> {'Online' if await AsyncConfigManager.get('other', 'project_active') else 'Offline'}\n"
            f"{icons.get("clock")} Старт проекта: {await AsyncConfigManager.get("other", "project_start_date")}\n"
            f"{icons.get("clock")} Сегодня: {datetime.today().strftime("%d.%m.%Y")}"
        ),
        parse_mode="HTML",
        reply_markup = await AdminKbs.mainPanelKb()
    )


# Bank

@router.callback_query(F.data == 'admin:bank', filters.IsAdmin())
async def OpenCBPanel(cb: CallbackQuery):
    cb_balance = await cryptobot.getBalance()
    await cb.message.edit_text(
        text=(
            f"{icons.get("cryptobot")} <b>Банк Meimun USDT</b>\n"
            f"{icons.get("wallet")} <b>Баланс:</b> <code>{cb_balance}</code>"
        ),
        parse_mode='HTML',
        reply_markup=await AdminKbs.bankPanelKb()
    )

@router.callback_query(F.data == 'admin:bank:add', filters.IsAdmin())
async def AddUSDTOnBalance(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.bankAddSum)
    await cb.message.edit_text(
        text=(
            f"{icons.get("cryptobot")} <b>Введите сумму для пополнения кассы</b>"
        ),
        parse_mode='HTML',
        reply_markup=await MainPage.backToMainKb("admin:main")
    )

@router.message(AdminStates.bankAddSum)
async def AddUSDTOnBalanceProc(msg: Message, state: FSMContext):
    if msg.text == "/start":
        await state.clear()
        return
    if not isinstance(float(msg.text), float):
        await msg.answer(
            text=(
                f"{icons.get("warning")}<b>Пожалуйста укажите число</b>"
            ),
            parse_mode='HTML',
            reply_markup=await MainPage.backToMainKb("admin:main")
        )
    invoice = await cryptobot.CreateInvoice(msg.text) 
    if invoice.get("url", "") != "":
        await msg.answer(
            text=f"{icons.get("cryptobot")} <b>Пополните по ссылке ниже</b>",
            parse_mode='HTML',
            reply_markup=await AdminKbs.PayUSDTKb(invoice.get("url"))
        )
    else:
        await msg.answer(
            text=(
                f"{icons.get("warning")}<b>Произошла неизвестная ошибка</b>"
            ),
            parse_mode='HTML',
            reply_markup=await MainPage.backToMainKb("admin:main")
        )


# Database Dump
@router.callback_query(F.data == 'admin:db_dump', filters.IsAdmin())
async def DumpDatabase(cb: CallbackQuery, state: FSMContext):
    link = await tempshhandler.upload_to_temp_sh(DATABASE_PATH)
    await cb.message.edit_text(
        text=f"{icons.get("download")} <b>Дамп БД:</b>",
        reply_markup=await AdminKbs.getBackupKb(link),
        parse_mode="HTML"
    )
    await cb.message.bot.send_message(
        chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
        text=(
            f"{icons.get("download")} <b>Дамп базы данных</b>\n"
            f"{icons.get("clock")} <b>Дата и время:</b> {datetime.now()}\n"
            f"{icons.get('link')} <b>Ссылка на бекап:</b>\n"
            f"{link}"
        ),
        parse_mode='HTML'
    )

# OP Controls
@router.callback_query(F.data == "admin:op", filters.IsAdmin())
async def OpenOPMenu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=(
            f"{icons.get("referrals")} <b>Управление ОП</b>\n\n"
        ),
        parse_mode="HTML",
        reply_markup= await AdminKbs.opControlMenuKb()
    )

@router.callback_query(F.data == "admin:op:backup", filters.IsAdmin())
async def BackupOpMenu(cb: CallbackQuery):
    await cb.message.edit_text(
        text=(
            f"{icons.get("download")} <b>Выберите тип бекапа</b>"
        ),
        reply_markup=await AdminKbs.chooseBackupTypeKb(),
        parse_mode='HTML'
    )

@router.callback_query(F.data == "admin:op:backup:pb", filters.IsAdmin())
async def BackupOpMenu(cb: CallbackQuery):
    async with session_maker() as session:
        data = await ophandler.dumpSponsorsInString(session)
        if data:
            link = await pastebinhandler.create_paste_simple(data, f"Meimun USDT Dump Sponsors - {datetime.now()}")
            await cb.message.edit_text(
                text=f"{icons.get("download")} <b>Бекап спонсоров:</b>",
                reply_markup=await AdminKbs.getBackupKb(link),
                parse_mode="HTML"
            )
            await cb.message.bot.send_message(
                chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
                text=(
                    f"{icons.get("download")} <b>Бекап спонсоров</b>\n"
                    f"{icons.get("clock")} <b>Дата и время:</b> {datetime.now()}\n"
                    f"{icons.get('link')} <b>Ссылка на бекап:</b>\n"
                    f"{link}"
                ),
                parse_mode='HTML'
            )
        else:
            await cb.message.answer(
                text=f"{icons.get("warning")} <b>Спонсоров нет или произошла ошибка</b>",
                parse_mode="HTML",
                reply_markup=await MainPage.backToMainKb("admin:main")
            )

@router.callback_query(F.data == "admin:op:backup:csv", filters.IsAdmin())
async def BackupOpMenu(cb: CallbackQuery):
    async with session_maker() as session:
        path = await ophandler.dumpSponsorsInCSV(session)
        if path:
            link = await tempshhandler.upload_to_temp_sh(path)
            await cb.message.edit_text(
                text=f"{icons.get("download")} <b>Бекап спонсоров:</b>",
                reply_markup=await AdminKbs.getBackupKb(link),
                parse_mode="HTML"
            )
            await cb.message.bot.send_message(
                chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
                text=(
                    f"{icons.get("download")} <b>Бекап спонсоров</b>\n"
                    f"{icons.get("clock")} <b>Дата и время:</b> {datetime.now()}\n"
                    f"{icons.get('link')} <b>Ссылка на бекап:</b>\n"
                    f"{link}"
                ),
                parse_mode='HTML'
            )
            os.remove(path)
        else:
            await cb.message.edit_text(
                text=f"{icons.get("warning")} <b>Спонсоров нет или произошла ошибка</b>",
                parse_mode="HTML",
                reply_markup=await MainPage.backToMainKb("admin:main")
            )

@router.callback_query(F.data == "admin:op:del", filters.IsAdmin())
async def AddNewOp(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.newop)
    await cb.message.edit_text(
        text=f"{icons.get("add")} <b>Для добавления спонсора укажите:</b>\nid",
        reply_markup=await MainPage.backToMainKb("admin:op"),
        parse_mode="HTML"
    )

@router.message(AdminStates.delop)
async def ProcessingNewOp(msg: Message, state: FSMContext):
    async with session_maker() as session:
        if not isinstance(int(msg.text), int):
            await msg.answer(
                text=f"{icons.get("warning")} <b>Неверный формат</b>\nid",
                parse_mode='HTML',
                reply_markup=await MainPage.backToMainKb("admin:op")
            )
        if msg.text:
            if await ophandler.delSponsor(session, int(msg.text)):  
                await msg.bot.send_message(
                    chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
                    text=(
                        f"{icons.get("referrals")} <b>Удален спонсор с ID - {msg.text}</b>"
                    ),
                    parse_mode='HTML'
                )
                await msg.answer(
                    text=(
                        f"{icons.get("referrals")} <b>Удален спонсор</b>\n"
                        f"{icons.get('link')} <b>ID:</b> {msg.text}\n"
                        f"{icons.get("robot")} <b>Удалил - @{msg.from_user.username}</b>"
                    ),
                    parse_mode='HTML',
                    reply_markup=await MainPage.backToMainKb("admin:main")
                )
            else:
                await msg.answer(
                    text=f"{icons.get("warning")} <b>Произошла ошибка</b>",
                    parse_mode='HTML',
                    reply_markup=await MainPage.backToMainKb("admin:op")
                )

@router.callback_query(F.data == "admin:op:add", filters.IsAdmin())
async def AddNewOp(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.newop)
    await cb.message.edit_text(
        text=f"{icons.get("add")} <b>Для добавления спонсора укажите:</b>\nссылка::срок::id",
        reply_markup=await MainPage.backToMainKb("admin:op"),
        parse_mode="HTML"
    )

@router.message(AdminStates.newop)
async def ProcessingNewOp(msg: Message, state: FSMContext):
    async with session_maker() as session:
        parts = msg.text.split("::")
        if len(parts) != 3:
            await msg.text(
                text=f"{icons.get("warning")} <b>Неверный формат</b>\nссылка::срок::id",
                parse_mode='HTML',
                reply_markup=await MainPage.backToMainKb("admin:op")
            )
        else:
            if await ophandler.addNewSponsor(session, parts[0], int(parts[1]), parts[2]):  
                await msg.bot.send_message(
                    chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
                    text=(
                        f"{icons.get("referrals")} <b>Добавлен спонсор</b>\n"
                        f"{icons.get('link')} <b>Ссылка:</b> {parts[0]}\n"
                        f"{icons.get("clock")} <b>Срок</b> {parts[1]} дней\n"
                        f"{icons.get("link")} <b>ID:</b> {parts[2]}"
                    ),
                    parse_mode='HTML'
                )
                await msg.answer(
                    text=(
                        f"{icons.get("referrals")} <b>Добавлен спонсор</b>\n"
                        f"{icons.get('link')} <b>Ссылка:</b> {parts[0]}\n"
                        f"{icons.get("clock")} <b>Срок</b> {parts[1]} дней\n"
                        f"{icons.get("link")} <b>ID:</b> {parts[2]}\n"
                        f"{icons.get("robot")} <b>Добавил - @{msg.from_user.username}</b>"
                    ),
                    parse_mode='HTML',
                    reply_markup=await MainPage.backToMainKb("admin:main")
                )
            else:
                await msg.answer(
                    text=f"{icons.get("warning")} <b>Произошла ошибка</b>",
                    parse_mode='HTML',
                    reply_markup=await MainPage.backToMainKb("admin:op")
                )

# User Controller
@router.callback_query(F.data == "admin:user", filters.IsAdmin())
async def OpenUserFoundMenu(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        await cb.message.edit_text(
            text=f"{icons.get("robot")} <b>Поиск пользователя, отправьте айди</b>",
            parse_mode="HTML",
            reply_markup = await MainPage.backToMainKb("admin:main")
        )
        await state.set_state(AdminStates.user_find_data)

@router.message(AdminStates.user_find_data, filters.IsAdmin())
async def FindUserProcess(msg: Message, state: FSMContext):
    async with session_maker() as session:
        user_data = await users_db.GetUserData(session, msg.text)
        if user_data['result']:
            await msg.answer(
                text=(
                    f"{icons.get("robot")} <b>Пользователь найден!</b>\n\n"
                    f"{icons.get("link")} <b>ID:</b> <code>{user_data.get("tgId", 'not found')}</code>\n"
                    f"{icons.get("profile")} <b>Username:</b> @{user_data.get("username", 'not found')}\n"
                    f"{icons.get("wallet")} <b>Баланс:</b> {round(user_data.get("balance", '?'), 2)}$\n"
                    f"{icons.get("brougthed_bucks")} <b>Вывел:</b> {round(user_data.get("brought", '?'), 2)}$\n"
                    f"{icons.get("referrals")} <b>Рефовод:</b> <code>{user_data.get("refId", '?')}</code>\n"
                    f"{icons.get("referrals")} <b>Рефералов:</b> {user_data.get("refs", '?')}\n"
                    f"{icons.get("warning")} <b>Статус блока:</b> {user_data.get("banStatus", '?')}\n"
                    f"{icons.get("clock")} <b>Ласт бонус:</b> {user_data.get("lastBonus", '?')}"
                ),
                parse_mode="HTML",
                reply_markup = await AdminKbs.fastUserMenuKb(msg.text)
            )
        else:
            await msg.answer(
                text=f"{icons.get("warning")} <b>Пользователь не найден</b>",
                parse_mode="HTML",
                reply_markup = await MainPage.backToMainKb("admin:user")
            )

@router.callback_query(F.data.regexp(r"^admin:user:ban"), filters.IsAdmin())
async def ChangeBanStatusForUser(cb: CallbackQuery):
    async with session_maker() as session:
        parts = cb.data.split(":")
        user_id = parts[3]
        await users_db.BanUnBanUser(session, user_id, cb.message.bot)
        user_data = await users_db.GetUserData(session, user_id)
        await cb.message.answer(
            text=(
                f"{icons.get("robot")} <b>Изменен статус бана!</b>\n\n"
                f"{icons.get("link")} <b>ID:</b> <code>{user_data.get("tgId", 'not found')}</code>\n"
                f"{icons.get("profile")} <b>Username:</b> @{user_data.get("username", 'not found')}\n"
                f"{icons.get("wallet")} <b>Баланс:</b> {round(user_data.get("balance", '?'), 2)}$\n"
                f"{icons.get("brougthed_bucks")} <b>Вывел:</b> {round(user_data.get("brought", '?'), 2)}$\n"
                f"{icons.get("referrals")} <b>Рефовод:</b> <code>{user_data.get("refId", '?')}</code>\n"
                f"{icons.get("referrals")} <b>Рефералов:</b> {user_data.get("refs", '?')}\n"
                f"{icons.get("warning")} <b>Статус блока:</b> {user_data.get("banStatus", '?')}\n"
                f"{icons.get("clock")} <b>Ласт бонус:</b> {user_data.get("lastBonus", '?')}"
            ),
            parse_mode="HTML",
            reply_markup = await AdminKbs.fastUserMenuKb(user_id)
        )

@router.callback_query(F.data.regexp(r"^admin:user:grm"), filters.IsAdmin())
async def ChangeBanStatusForUser(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        parts = cb.data.split(":")
        user_id = parts[3]
        await state.set_state(AdminStates.attached_user_id)
        await state.update_data(attached_user_id=user_id)
        await cb.message.edit_text(
            text=f"{icons.get("brougthed_bucks")} <b>Введите сумму которую нужно забрать у пользователя</b>",
            parse_mode='HTML',
            reply_markup = await MainPage.backToMainKb("admin:user")
        )
        await state.set_state(AdminStates.user_change_money_m_data)
        
@router.message(AdminStates.user_change_money_m_data, filters.IsAdmin())
async def MinusFromUserBalance(msg: Message, state: FSMContext):
    async with session_maker() as session:
        data = await state.get_data()
        if isinstance(float(msg.text), float):
            user_id = data.get("attached_user_id")
            await financial.MinusMoney(session, user_id, float(msg.text))
            user_data = await users_db.GetUserData(session, user_id)
            await msg.answer(
                text=(
                    f"{icons.get("robot")} <b>Изменен статус бана!</b>\n\n"
                    f"{icons.get("link")} <b>ID:</b> <code>{user_data.get("tgId", 'not found')}</code>\n"
                    f"{icons.get("profile")} <b>Username:</b> @{user_data.get("username", 'not found')}\n"
                    f"{icons.get("wallet")} <b>Баланс:</b> {round(user_data.get("balance", '?'), 2)}$\n"
                    f"{icons.get("brougthed_bucks")} <b>Вывел:</b> {round(user_data.get("brought", '?'), 2)}$\n"
                    f"{icons.get("referrals")} <b>Рефовод:</b> <code>{user_data.get("refId", '?')}</code>\n"
                    f"{icons.get("referrals")} <b>Рефералов:</b> {user_data.get("refs", '?')}\n"
                    f"{icons.get("warning")} <b>Статус блока:</b> {user_data.get("banStatus", '?')}\n"
                    f"{icons.get("clock")} <b>Ласт бонус:</b> {user_data.get("lastBonus", '?')}"
                ),
                parse_mode="HTML",
                reply_markup = await AdminKbs.fastUserMenuKb(user_id)
            )

@router.callback_query(F.data.regexp(r"^admin:user:gim"), filters.IsAdmin())
async def ChangeBanStatusForUser(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        parts = cb.data.split(":")
        user_id = parts[3]
        await state.set_state(AdminStates.attached_user_id)
        await state.update_data(attached_user_id=user_id)
        await cb.message.edit_text(
            text=f"{icons.get("brougthed_bucks")} <b>Введите сумму которую нужно добавить пользователю</b>",
            parse_mode='HTML',
            reply_markup = await MainPage.backToMainKb("admin:user")
        )
        await state.set_state(AdminStates.user_change_money_p_data)
        
@router.message(AdminStates.user_change_money_p_data, filters.IsAdmin())
async def MinusFromUserBalance(msg: Message, state: FSMContext):
    async with session_maker() as session:
        data = await state.get_data()
        if isinstance(float(msg.text), float):
            user_id = data.get("attached_user_id")
            await financial.AddMoney(session, user_id, float(msg.text))
            user_data = await users_db.GetUserData(session, user_id)
            await msg.answer(
                text=(
                    f"{icons.get("robot")} <b>Изменен статус бана!</b>\n\n"
                    f"{icons.get("link")} <b>ID:</b> <code>{user_data.get("tgId", 'not found')}</code>\n"
                    f"{icons.get("profile")} <b>Username:</b> @{user_data.get("username", 'not found')}\n"
                    f"{icons.get("wallet")} <b>Баланс:</b> {round(user_data.get("balance", '?'), 2)}$\n"
                    f"{icons.get("brougthed_bucks")} <b>Вывел:</b> {round(user_data.get("brought", '?'), 2)}$\n"
                    f"{icons.get("referrals")} <b>Рефовод:</b> <code>{user_data.get("refId", '?')}</code>\n"
                    f"{icons.get("referrals")} <b>Рефералов:</b> {user_data.get("refs", '?')}\n"
                    f"{icons.get("warning")} <b>Статус блока:</b> {user_data.get("banStatus", '?')}\n"
                    f"{icons.get("clock")} <b>Ласт бонус:</b> {user_data.get("lastBonus", '?')}"
                ),
                parse_mode="HTML",
                reply_markup = await AdminKbs.fastUserMenuKb(user_id)
            )

# Stats
@router.callback_query(F.data == "admin:stats", filters.IsAdmin())
async def OpenAdminStatsMenu(cb: CallbackQuery):
    async with session_maker() as session:
        total_balances = await financial.getTotalBalances(session)
        total_withdrawal = await financial.getTotalWithdrawal(session)
        total_users = await users_db.HowManyUsersInSystem(session)
        money_for_withdraw = await financial.getTotalMoneyForWithdraw(session)
        total_refs = await users_db.HowManyRefsInSystem(session)
        total_requests_in_sleep = await withdraws.GetTotalRequestsOnSleep(session)
        total_requests_successfull = await withdraws.GetTotalRequests(session)
        await cb.message.edit_text(
            text=(
                f"{icons.get("stats")} <b>Статистика бота</b>\n\n"
                f"{icons.get("profile")} <b>Юзеров:</b> {total_users}\n"
                f"{icons.get("referrals")} <b>Рефералов</b> {total_refs}\n\n"
                f"{icons.get("wallet")} <b>У юзеров:</b> {round(total_balances, 2)}$\n"
                f"{icons.get("brougthed_bucks")} <b>Вывели:</b> {round(total_withdrawal, 2)}$\n"
                f"{icons.get("brougthed_bucks")} <b>На выводе:</b> {round(money_for_withdraw, 2)}$\n"
                f"{icons.get("link")} <b>Заявок на вывод:</b> {total_requests_in_sleep}\n"
                f"{icons.get("accept")} <b>Отработали:</b> {total_requests_successfull} заявок\n"
            ),
            parse_mode="HTML",
            reply_markup = await MainPage.backToMainKb("admin:main")
        )

# Ads
@router.callback_query(F.data == "admin:ads", filters.IsAdmin())
async def OpenAdsMenu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"{icons.get("robot")} <b>Пожалуйста введите текст рассылки</b>",
        parse_mode="HTML",
        reply_markup = await MainPage.backToMainKb("admin:main")
    )
    await state.set_state(AdminStates.piar_data)

@router.message(AdminStates.piar_data, filters.IsAdmin())
async def ProccessingData(msg: Message, state: FSMContext):
    await state.update_data(piar_data=msg.text)
    await msg.answer(
        text=f"{icons.get("stop")} Стоп! Проверьте, все верно?\n<pre>Data\n{msg.text}</pre>",
        parse_mode="HTML",
        reply_markup = await AdminKbs.checkAdsMessage()
    )

@router.callback_query(F.data == "admin:ads:a", filters.IsAdmin())
async def AcceptAndSendAdMsg(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        data = await state.get_data()
        msg = data.get("piar_data")
        if msg is not None:
            users_list = await users_db.dumpUsersIdInList(session)
            if len(users_list) > 0:
                sended_for_x_users = 0
                error_on_send = 0
                successfull_sends = 0
                for user_id in users_list:
                    try:
                        await cb.message.bot.send_message(
                            chat_id=user_id,
                            text=msg,
                            parse_mode="HTML"
                        )
                        successfull_sends = successfull_sends + 1
                    except Exception as ex:
                        error_on_send = error_on_send + 1
                        print(f"OnSendAdMessageError: ID: {user_id}: Error: {ex}")
                    sended_for_x_users = sended_for_x_users + 1
                    await cb.message.edit_text(
                        text=f"{icons.get("robot")} <b>Рассылка сообщений {sended_for_x_users}/{len(users_list)}</b>\n{icons.get("accept")}{successfull_sends} {icons.get("bad")}{error_on_send}",
                        parse_mode="HTML"
                    )
                await cb.message.edit_text(
                    text=f"{icons.get("accept")} <b>Рассылка успешно закончилась</b>",
                    parse_mode="HTML",
                    reply_markup = await MainPage.backToMainKb("admin:main")
                )
            else:
                await cb.message.edit_text(
                    text=f"{icons.get("robot")} <b>Ошибка при получении ID юзеров </b>",
                    parse_mode="HTML",
                    reply_markup = await MainPage.backToMainKb("admin:main")
                )
        else:
            await cb.message.edit_text(
                text=f"{icons.get("robot")} <b>Неизвестная ошибка</b>",
                parse_mode="HTML",
                reply_markup = await MainPage.backToMainKb("admin:main")
            )


@router.callback_query(F.data == "admin:ads:c", filters.IsAdmin())
async def AcceptAndSendAdMsg(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        await state.clear()
        await cb.message.edit_text(
            text=f"{icons.get("accept")} <b>Рассылка отменена</b>",
            parse_mode="HTML",
            reply_markup = await MainPage.backToMainKb("admin:main")
        )

# Config
@router.callback_query(F.data == "admin:cfg", filters.IsAdmin())
async def OpenConfigMenu(cb: CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        jsonInString = await AsyncConfigManager.backup()
        await cb.message.edit_text(
            text=(
                f"<b>{icons.get("code")} Настройки конфига</b>\n\n"
                f"<b>{icons.get('active' if await AsyncConfigManager.get('other', 'project_active') else 'nonactive')} Статус:</b> {'Online' if await AsyncConfigManager.get('other', 'project_active') else 'Offline'}\n"
                f"<pre>ActiveConfig.json\n{jsonInString}\n</pre>"
            ),
            parse_mode='HTML',
            reply_markup = await AdminKbs.configMenuKb(await AsyncConfigManager.get('other', 'project_active'))
        )

@router.callback_query(F.data == "admin:cfg:turn", filters.IsAdmin())
async def TurnOnBot(cb: CallbackQuery):
    await AsyncConfigManager.set(True, "other", "project_active")
    activity_status_now = await AsyncConfigManager.get("other", "project_active")
    if activity_status_now:
        await cb.answer("Бот успешно включился!")
        jsonInString = await AsyncConfigManager.backup()
        await cb.message.edit_text(
            text=(
                f"<b>{icons.get("code")} Настройки конфига</b>\n\n"
                f"<pre>ActiveConfig.json\n{jsonInString}\n</pre>"
            ),
            parse_mode='HTML',
            reply_markup = await AdminKbs.configMenuKb(await AsyncConfigManager.get('other', 'project_active'))
        )
    else:
        await cb.answer("Произошла ошибка, попробуйте позже вновь")

@router.callback_query(F.data == "admin:cfg:turnoff", filters.IsAdmin())
async def TurnOnBot(cb: CallbackQuery):
    await AsyncConfigManager.set(False, "other", "project_active")
    activity_status_now = await AsyncConfigManager.get("other", "project_active")
    if not activity_status_now:
        await cb.answer("Бот успешно выключился!")
        jsonInString = await AsyncConfigManager.backup()
        await cb.message.edit_text(
            text=(
                f"<b>{icons.get("code")} Настройки конфига</b>\n\n"
                f"<pre>ActiveConfig.json\n{jsonInString}\n</pre>"
            ),
            parse_mode='HTML',
            reply_markup = await AdminKbs.configMenuKb(await AsyncConfigManager.get('other', 'project_active'))
        )
    else:
        await cb.answer("Произошла ошибка, попробуйте позже вновь")

@router.callback_query(F.data == "admin:cfg:replace", filters.IsAdmin())
async def OpenReplaceConfigMenu(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.json_data)
    await cb.message.edit_text(
        text=(
            f"{icons.get("code")} <b>Отправьте новый конфиг следующим сообщением</b>"
        ),
        reply_markup = await MainPage.backToMainKb("admin:main"),
        parse_mode="HTML"
    )

@router.message(AdminStates.json_data)
async def ReplaceConfigProcess(msg: Message, state: FSMContext):
    await state.update_data(json_data=msg.text)
    await msg.answer(
        text=(
            f"{icons.get("warning")}<b>Проверьте!</b>\n\n"
            f"<pre>NewConfig.json\n{msg.text}\n</pre>"
        ),
        parse_mode="HTML",
        reply_markup = await AdminKbs.acceptConfigReplaceKb()
    )

@router.callback_query(F.data == "admin:cfg:replace:a", filters.IsAdmin())
async def AcceptAndReplaceConfig(cb: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    newcfg = state_data.get("json_data", None)
    if newcfg:
        adminChatId = await AsyncConfigManager.get("admins", "admins_chat")
        await cb.message.bot.send_message(
            chat_id=adminChatId,
            text=(
                f"{icons.get("warning")}<b>Обновлен конфиг</b>\n"
                f"{icons.get("profile")}<b>Обновил - @{cb.from_user.username}\n\n</b>"
                f"<pre>NewConfig.json\n{newcfg}\n</pre>"
            ),
            parse_mode="HTML"
        )
        await cb.message.edit_text(
            text=f"{icons.get("accept")} <b>Конфиг обновлен</b>",
            reply_markup = await MainPage.backToMainKb("admin:main"),
            parse_mode="HTML"
        )
        await AsyncConfigManager.replace(newcfg)
        await state.clear()
    else:
        await cb.message.edit_text(
            text=f"{icons.get("warning")} <b>Произошла ошибка при попытке обновления</b>",
            parse_mode="HTML",
            reply_markup = await MainPage.backToMainKb("admin:main")
        )
        await state.clear()

@router.callback_query(F.data == "admin:cfg:replace:c", filters.IsAdmin())
async def CancelReplaceConfig(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.edit_text(
        text=f"{icons.get("accept")} <b>Успешная отмена изменения конфига</b>",
        parse_mode="HTML",
        reply_markup = await MainPage.backToMainKb("admin:main")
    )

@router.callback_query(F.data == "admin:cfg:price", filters.IsAdmin())
async def OpenChangePricesMenu(cb: CallbackQuery):
    minWithdrawPrice = await AsyncConfigManager.get("withdraw", "min_cb_withdraw")
    refBonus = await AsyncConfigManager.get("bonuses", "ref_bonus")
    dailyBonus = await AsyncConfigManager.get("bonuses", "daily_bonus")
    activity_status = await AsyncConfigManager.get("other", "project_active")
    refWarn = await AsyncConfigManager.get("sponsors", "unsubed_warn_price")
    await cb.message.edit_text(
        text=(
            f"{icons.get("wallet")} <b>Изменение прайса</b>\n\n"
            f"{icons.get("brougthed_bucks")} <b>Мин. вывод:</b> <code>{minWithdrawPrice}$</code>\n"
            f"{icons.get("referrals")} <b>Реф. бонус:</b> <code>{refBonus}$</code>\n"
            f"{icons.get("warning")} <b>Реф. штраф:</b> <code>{refWarn}$</code>\n"
            f"{icons.get("bonus")} <b>Еж. бонус:</b> <code>{dailyBonus}$</code>"
        ),
        reply_markup=await AdminKbs.changePricesKb(activity_status),
        parse_mode='HTML'
    )

@router.callback_query(F.data == "admin:cfg:price:rw", filters.IsAdmin())
async def ChangeMinWithdraw(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"{icons.get("bonus")} <b>Отправьте новый реф. штраф следующим сообщением</b>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.price_data_rw)

@router.message(AdminStates.price_data_rw)
async def ChangeMinWithdrawFinish(msg: Message, state: FSMContext):
    if isinstance(float(msg.text), float):
        await AsyncConfigManager.set(float(msg.text), "sponsors", "unsubed_warn_price")
        await msg.answer(
            text=f"{icons.get("brougthed_bucks")} <b>Реф. штраф изменен на - {float(msg.text)}$</b>",
            parse_mode='HTML',
            reply_markup=await MainPage.backToMainKb("admin:main")
        )
        await msg.bot.send_message(
            chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
            text=f"{icons.get("brougthed_bucks")} <b>Реф. штраф обновлен на - {float(msg.text)}$</b>\n{icons.get("profile")} <b>Обновил</b> - @{msg.from_user.username}",
            parse_mode='HTML'
        )

@router.callback_query(F.data == "admin:cfg:price:mw", filters.IsAdmin())
async def ChangeMinWithdraw(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"{icons.get("bonus")} <b>Отправьте новый мин. вывод следующим сообщением</b>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.price_data_mw)

@router.message(AdminStates.price_data_mw)
async def ChangeMinWithdrawFinish(msg: Message, state: FSMContext):
    if isinstance(float(msg.text), float):
        await AsyncConfigManager.set(float(msg.text), "withdraw", "min_cb_withdraw")
        await msg.answer(
            text=f"{icons.get("brougthed_bucks")} <b>Мин. вывод изменен на - {float(msg.text)}$</b>",
            parse_mode='HTML',
            reply_markup=await MainPage.backToMainKb("admin:main")
        )
        await msg.bot.send_message(
            chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
            text=f"{icons.get("brougthed_bucks")} <b>Мин. вывод обновлен на - {float(msg.text)}$</b>\n{icons.get("profile")} <b>Обновил</b> - @{msg.from_user.username}",
            parse_mode='HTML'
        )

@router.callback_query(F.data == "admin:cfg:price:rb", filters.IsAdmin())
async def ChangeRefBonus(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"{icons.get("bonus")} <b>Отправьте новый реф. бонус следующим сообщением</b>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.price_data_rb)

@router.message(AdminStates.price_data_rb)
async def ChangeRefBonusFinish(msg: Message, state: FSMContext):
    if isinstance(float(msg.text), float):
        try:
            await AsyncConfigManager.set(float(msg.text), "bonuses", "ref_bonus")
        except Exception as ex:
            print(ex)
        await msg.answer(
            text=f"{icons.get("referrals")} <b>Реф. бонус изменен на - {float(msg.text)}$</b>",
            parse_mode='HTML',
            reply_markup=await MainPage.backToMainKb("admin:main")
        )
        await msg.bot.send_message(
            chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
            text=f"{icons.get("referrals")} <b>Реф. бонус обновлен на - {float(msg.text)}$</b>\n{icons.get("profile")} <b>Обновил</b> - @{msg.from_user.username}",
            parse_mode='HTML'
        )

@router.callback_query(F.data == "admin:cfg:price:db", filters.IsAdmin())
async def ChangeDailyBonus(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"{icons.get("bonus")} <b>Отправьте новый еж. бонус следующим сообщением</b>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.price_data_db)

@router.message(AdminStates.price_data_db)
async def ChangeDailyBonusFinish(msg: Message, state: FSMContext):
    if isinstance(float(msg.text), float):
        await AsyncConfigManager.set(float(msg.text), "bonuses", "daily_bonus")
        await msg.answer(
            text=f"{icons.get("bonus")} <b>Еж. бонус изменен на - {float(msg.text)}$</b>",
            parse_mode='HTML',
            reply_markup=await MainPage.backToMainKb("admin:main")
        )
        await msg.bot.send_message(
            chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
            text=f"{icons.get("bonus")} <b>Еж. бонус обновлен на - {float(msg.text)}$</b>\n{icons.get("profile")} <b>Обновил</b> - @{msg.from_user.username}",
            parse_mode='HTML'
        )

# Promocodes
@router.callback_query(F.data == "admin:promo", filters.IsAdmin())
async def OpenPromocodesMenu(cb: CallbackQuery):
    await cb.message.edit_text(
        text=f"{icons.get("robot")}<b>Выберите действие:</b>",
        parse_mode="HTML",
        reply_markup = await AdminKbs.promocodesPanelKb()
    )

@router.callback_query(F.data == "admin:promo:del", filters.IsAdmin())
async def OpenPromocodesDelMenu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"{icons.get("robot")}<b>Введите ID промокода для удаления</b>",
        parse_mode="HTML",
        reply_markup = await MainPage.backToMainKb("admin:main")
    )
    await state.set_state(AdminStates.promocode_id_for_del)

@router.message(AdminStates.promocode_id_for_del, filters.IsAdmin())
async def OpenPromocodesDelMenu(msg: Message, state: FSMContext):
    async with session_maker() as session:
        try:
            if isinstance(int(msg.text), int):
                await msg.answer(
                    text=f"{icons.get("clock")} <b>Поиск промокода по ID...</b>",
                    parse_mode="HTML"
                )
                promocode = await promocodes.findPromocodeById(session, int(msg.text))
                if promocode["result"]:
                    await msg.answer(
                        text=f"{icons.get("robot")} <b>Промокод найден:</b>\n{icons.get("link")}<b>ID:</b> {msg.text}\n{icons.get("code")}<b>Promocode:</b> {promocode.get("promocode", "empty")}\n{icons.get("bonus")}<b>Prize:</b> {icons.get("prize")}\n{icons.get("referrals")}<b>Activates:</b> {icons.get("activates")}",
                        reply_markup = await AdminKbs.getPromocodeInfoKb(msg.text),
                        parse_mode="HTML"
                    )
                else:
                    await msg.answer(
                        text=f"{icons.get("warning")} <b>Произошла ошибка при поиске промокода</b>",
                        reply_markup = await MainPage.backToMainKb("admin:promo"),
                        parse_mode="HTML"
                    )
        except Exception as ex:
            await msg.answer(
                text=f"{icons.get("warning")} <b>Произошла ошибка при поиске промокода</b>",
                reply_markup = await MainPage.backToMainKb("admin:promo"),
                parse_mode="HTML"
            )

@router.callback_query(F.data.regexp(r"^admin:promo:a_d"), filters.IsAdmin())
async def AcceptAndDeletePromocode(cb: CallbackQuery):
    
    async with session_maker() as session:
        parts = cb.data.split(":")
        promo_id = parts[3]
        await cb.message.edit_text(
            text=f"{icons.get("clock")} <b>Удаление промокода №{promo_id}</b>",
            parse_mode='HTML'
        )
        promo_data = await promocodes.findPromocodeById(session, promo_id)
        if await promocodes.delPromo(session, promo_id):
            await cb.message.bot.send_message(
                chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
                text=(
                    f"{icons.get("warning")} <b>Удален промокод!</b>\n\n"
                    f"{icons.get("link")} <b>ID:</b> {promo_id}\n"
                    f"{icons.get("code")} <b>Promocode:</b> {promo_data.get("promocode", "empty")}\n\n"
                    f"<i>Удалил @{cb.from_user.username}</i>"
                ),
                parse_mode="HTML"
            )
            await cb.message.edit_text(
                text=f"{icons.get("accept")} <b>Успешное удаление промокода №{promo_id}</b>",
                parse_mode="HTML",
                reply_markup = await MainPage.backToMainKb("admin:promo")
            )
        else:
            await cb.message.edit_text(
                text=f"{icons.get("bad")} <b>Ошибка при удалении промокода №{promo_id}</b>",
                parse_mode="HTML",
                reply_markup = await MainPage.backToMainKb("admin:promo")
            )

@router.callback_query(F.data == "admin:promo:dump", filters.IsAdmin())
async def OpenPromocodesDumpMenu(cb: CallbackQuery):
    await cb.message.edit_text(
        text=f"{icons.get("robot")} <b>Выберите формат:</b>",
        parse_mode="HTML",
        reply_markup = await AdminKbs.chooseDumpTypeKb()
    )

@router.callback_query(F.data == "admin:promo:dump:csv", filters.IsAdmin())
async def OpenPromocodesDumpMenu(cb: CallbackQuery):
    await cb.message.edit_text(
        text=f"{icons.get("stop")} <b>Not Worked Now!</b>",
        parse_mode="HTML",
        reply_markup = await MainPage.backToMainKb("admin:main")
    )

@router.callback_query(F.data == "admin:promo:dump:pastebin", filters.IsAdmin())
async def OpenPromocodesDumpMenu(cb: CallbackQuery):
    async with session_maker() as session:
        await cb.message.edit_text(
            text=f"{icons.get("clock")} <b>Пожалуйста подождите...</b>",
            parse_mode="HTML",
            reply_markup = await AdminKbs.promocodesPanelKb()
        )
        data = await promocodes.dumpFullTable(session)
        link = await pastebinhandler.create_paste_simple(data, f"Promocodes Dump - {datetime.now()}")
        await cb.message.edit_text(
            text=f"{icons.get("robot")} <b>Успешный дамп!</b>\n{link}"
        )

@router.callback_query(F.data == "admin:promo:add", filters.IsAdmin())
async def OpenPromocodesMenu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        text=f"<b>Создание промокода:</b>\n\nДля создания отправьте параметры в формате\nпромокод::активации::награда",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.new_promocode_form)

@router.message(AdminStates.new_promocode_form)
async def ProcessingNewPromocode(msg: Message, state: FSMContext):
    async with session_maker() as session:
        try: 
            parts = msg.text.split("::")
            if len(parts) != 3:
                await msg.answer(
                    text=f"Для создания отправьте параметры в формате\nпромокод::активации::награда",
                    parse_mode="HTML"
                )
                return
            if isinstance(int(parts[1]), int) and isinstance(int(parts[2]), int):
                await promocodes.createPromo(session, parts[0], parts[1], parts[2])
                await msg.bot.send_message(
                    chat_id=await AsyncConfigManager.get("admins", "admins_chat"),
                    text=(
                        f"{icons.get("robot")} <b>Создан новый промокод</b>\n\n"
                        f"<b>Промокод:</b> {parts[0]}\n"
                        f"<b>Активаций:</b> {parts[1]}\n"
                        f"<b>Приз:</b> {parts[2]}$\n\n"
                        f"<b>Создал @{msg.from_user.username}</b>"
                    ),
                    parse_mode="HTML"
                )
                await msg.answer(
                    text=f"<b>Промокод <i>{parts[0]}</i> успешно создан!</b>",
                    parse_mode="HTML",
                    reply_markup = await MainPage.backToMainKb("admin:main")
                )
        except Exception as ex:
            await msg.answer(
                text=f"{icons.get("stop")} Error:\n{ex}",
                parse_mode="HTML"
            )

# Withdraw Requests
@router.callback_query(F.data.regexp(r"^admin:a_r"), filters.IsAdmin())
async def AcceptWithdrawRequest(cb: CallbackQuery):
    async with session_maker() as session:
        parts = cb.data.split(":")
        request_id = parts[2]
        result = await withdraws.ChangeRequestStatus(session, request_id, True)
        if result:
            request_data = await withdraws.GetRequestData(session, request_id)
            check = await cryptobot.CreateWithdrawCheck(request_data["sum"], request_data["tgid"])
            await cb.message.bot.send_sticker(
                chat_id=request_data["tgid"],
                sticker="CAACAgEAAxkBAAICOml-Q3D-pyf56go8YZ3Q-c8neev9AAIdAQACOA6CEeGEiSFq5-6JOAQ"
            )
            await cb.message.bot.send_message(
                chat_id=request_data["tgid"],
                text=f"{icons.get("congratulations")} <b>Вывод одобрен! Вы можете забрать свои деньги нажав на кнопку.</b>",
                parse_mode="HTML",
                reply_markup = await AdminKbs.getBrougthedMoneysKb(check)
            )
            await cb.message.edit_text(
                text=(
                    f"{icons.get("accept")} <b>Заявка одобрена</b>\n\n"
                    f"{icons.get("robot")} <b>Одобрил:</b> @{cb.from_user.username}\n"
                    f"{icons.get("profile")} <b>Юзер:</b> {request_data["tgid"]}\n"
                    f"{icons.get("code")} <b>RID:</b> {request_id}\n"
                    f"{icons.get("wallet")} <b>Сумма:</b> {request_data["sum"]}$\n"
                ),
                parse_mode="HTML"
            )
            masked_user = f"{str(request_data['tgid'])[:3]}***{str(request_data['tgid'])[-3:]}"
            await cb.message.bot.send_message(
                chat_id=await AsyncConfigManager.get('admins', 'payots_chat'),
                text=(
                    f"{icons.get("brougthed_bucks")} <b>Новая выплата</b>\n"
                    f"{icons.get("profile")} <b>Пользователь:</b> {masked_user}\n"
                    f"{icons.get("wallet")} <b>Сумма:</b> {request_data['sum']} USDT\n"
                    f"{icons.get("accept")} <i>Заявка успешно обработана.</i>"
                ),
                parse_mode='HTML'
            )

@router.callback_query(F.data.regexp(r"^admin:c_r"), filters.IsAdmin())
async def CancelWithdrawRequest(cb: CallbackQuery):
    async with session_maker() as session:
        parts = cb.data.split(":")
        request_id = parts[2]
        result = await withdraws.ChangeRequestStatus(session, request_id, False)
        if result:
            request_data = await withdraws.GetRequestData(session, request_id)
            await cb.message.bot.send_sticker(
                chat_id=request_data["tgid"],
                sticker="CAACAgEAAxkBAAICPml-Q4iXvdFjsmUv9QOJMqb6_NMkAAIkAQACOA6CEfFS_5iGswZcOAQ"
            )
            await cb.message.bot.send_message(
                chat_id=request_data["tgid"],
                text=f"{icons.get("bad")} <b>Вывод отклонен! Мы вернули деньги на ваш баланс</b>",
                parse_mode="HTML"
            )
            await cb.message.edit_text(
                text=(
                    f"{icons.get("accept")} <b>Заявка отклонена</b>\n\n"
                    f"{icons.get("robot")} <b>Отклонил:</b> @{cb.from_user.username}\n"
                    f"{icons.get("profile")} <b>Юзер:</b> {request_data["tgid"]}\n"
                    f"{icons.get("code")} <b>RID:</b> {request_id}\n"
                    f"{icons.get("wallet")} <b>Сумма:</b> {request_data["sum"]}$\n"
                ),
                parse_mode="HTML"
            )
            await financial.AddMoney(session, request_data['tgid'], request_data['sum'])
