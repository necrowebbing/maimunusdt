
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class AdminKbs():
    async def bankPanelKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Пополнить", callback_data=f"admin:bank:add", icon_custom_emoji_id="5931614414351372818"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")

            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def AddUSDTKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Пополнить", callback_data=f"admin:bank:add", icon_custom_emoji_id="5931614414351372818"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data=f"admin:main", icon_custom_emoji_id="5960671702059848143")

            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def PayUSDTKb(link):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Пополнить", url=link, icon_custom_emoji_id="5931614414351372818"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data=f"admin:main", icon_custom_emoji_id="5960671702059848143")

            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def mainPanelKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Промокоды", callback_data=f"admin:promo", icon_custom_emoji_id="6032644646587338669"),
                InlineKeyboardButton(text="Рассылка", callback_data=f"admin:ads", icon_custom_emoji_id="6028171274939797252")
            ],
            [
                InlineKeyboardButton(text="Статистика", callback_data=f"admin:stats", icon_custom_emoji_id="5938539885907415367")
            ],
            [
                InlineKeyboardButton(text="Поиск Юзера", callback_data=f"admin:user", icon_custom_emoji_id="5942826671290715541")
            ],
            [
                InlineKeyboardButton(text="ОП", callback_data=f"admin:op", icon_custom_emoji_id="6032594876506312598"),
                InlineKeyboardButton(text="КФГ", callback_data=f"admin:cfg", icon_custom_emoji_id="5877260593903177342")
            ],
            [
                InlineKeyboardButton(text='Дамп БД', callback_data=f"admin:db_dump", icon_custom_emoji_id='5877307202888273539'),
                InlineKeyboardButton(text='Банк', callback_data=f"admin:bank", icon_custom_emoji_id='5807465992363710697')
            ],
            [
                InlineKeyboardButton(text="Обычное меню", callback_data=f"open:main", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    
    async def configMenuKb(activity_status: bool):
        if activity_status:
            inline_kb_list = [
                [
                    InlineKeyboardButton(text="Изменить прайс", callback_data=f"admin:cfg:price")
                ],
                [
                    InlineKeyboardButton(text="Изменить конфиг", callback_data=f"admin:cfg:replace")
                ],
                [
                    InlineKeyboardButton(text="Выключить бота", callback_data=f"admin:cfg:turnoff")
                ],
                [
                    InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
                ]
            ]
            return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
        else:
            inline_kb_list = [
                [
                    InlineKeyboardButton(text="Изменить прайс", callback_data=f"admin:cfg:price")
                ],
                [
                    InlineKeyboardButton(text="Изменить конфиг", callback_data=f"admin:cfg:replace")
                ],
                [
                    InlineKeyboardButton(text="Включить бота", callback_data=f"admin:cfg:turn")
                ],
                [
                    InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
                ]
            ]
            return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def acceptConfigReplaceKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Заменить", callback_data=f"admin:cfg:replace:a", style="success", icon_custom_emoji_id="5825794181183836432"),
                InlineKeyboardButton(text="Отмена", callback_data=f"admin:cfg:replace:c", style="danger", icon_custom_emoji_id="5778527486270770928")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def opControlMenuKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Добавить", callback_data=f"admin:op:add", icon_custom_emoji_id="5931614414351372818"),
                InlineKeyboardButton(text="Удалить", callback_data=f"admin:op:del", icon_custom_emoji_id="5879896690210639947")
            ],
            [
                InlineKeyboardButton(text="Бекап", callback_data=f"admin:op:backup", icon_custom_emoji_id="5877307202888273539")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def chooseBackupTypeKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="pastebin", callback_data=f"admin:op:backup:pb"),
                InlineKeyboardButton(text="csv", callback_data=f"admin:op:backup:csv")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def getBackupKb(link: str):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Получить", url=link)
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def changePricesKb(activity_status: bool):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Еж. бонус", callback_data=f"admin:cfg:price:db", icon_custom_emoji_id="6032644646587338669"),
                InlineKeyboardButton(text="Реф. бонус", callback_data=f"admin:cfg:price:rb", icon_custom_emoji_id="6032594876506312598")
            ],
            [
                InlineKeyboardButton(text="Мин. вывод", callback_data=f"admin:cfg:price:mw", icon_custom_emoji_id="5987880246865565644")
            ],
            [
                InlineKeyboardButton(text="Реф. штраф", callback_data=f"admin:cfg:price:rw", icon_custom_emoji_id="6030563507299160824")
            ],
            [
                InlineKeyboardButton(text="Выключить бота", callback_data=f"admin:cfg:shutup", icon_custom_emoji_id="5920482576379679165")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
            ]        
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def fastUserMenuKb(tgid):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Give USDT", callback_data=f"admin:user:gim:{tgid}", icon_custom_emoji_id="5807465992363710697"),
                InlineKeyboardButton(text="Get USDT", callback_data=f"admin:user:grm:{tgid}", icon_custom_emoji_id="5987880246865565644"),
            ],
            [
                InlineKeyboardButton(text="Ban/Unban", callback_data=f"admin:user:ban:{tgid}", icon_custom_emoji_id="5309789538862774805")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")

            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def promocodesPanelKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Дамп", callback_data=f"admin:promo:dump", icon_custom_emoji_id="5877307202888273539"),
                InlineKeyboardButton(text="Создать", callback_data=f"admin:promo:add", icon_custom_emoji_id="5931614414351372818")
            ],
            [
                InlineKeyboardButton(text="Поиск", callback_data=f"admin:promo:del", icon_custom_emoji_id="5874960879434338403")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")

            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def chooseDumpTypeKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="pastebin", callback_data=f"admin:promo:dump:pastebin", icon_custom_emoji_id="6028171274939797252")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="admin:main", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def requestHandlersKb(request_id: int):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Вывод", callback_data=f"admin:a_r:{request_id}", icon_custom_emoji_id="5825794181183836432", style="success"),   
                InlineKeyboardButton(text="Отмена", callback_data=f"admin:c_r:{request_id}", icon_custom_emoji_id="5778527486270770928", style="danger")    
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def getBrougthedMoneysKb(link: str):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Получить", url=link, icon_custom_emoji_id="5987880246865565644")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    
    async def checkAdsMessage():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Отправить", style="success", callback_data=f"admin:ads:a", icon_custom_emoji_id="5875180111744995604")
            ],
            [
                InlineKeyboardButton(text="Отмена", style="danger", callback_data="admin:ads:c", icon_custom_emoji_id="5960671702059848143")
            ]

        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def getPromocodeInfoKb(id):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Удалить", callback_data=f"admin:promo:a_d:{id}", icon_custom_emoji_id="5940433880585605708", style="danger")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", callback_data=f"admin:promo", icon_custom_emoji_id="5960671702059848143", style="primary")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    
