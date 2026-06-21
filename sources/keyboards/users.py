
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sources.utils.configmanager import AsyncConfigManager

class MainPage:
    async def mainKb(userid):
        ADMINS_LIST = await AsyncConfigManager.get("admins", "admins_list")
        if userid in ADMINS_LIST:
            inline_kb_list = [
                [
                    InlineKeyboardButton(text="Рефералы", callback_data=f"open:refs", icon_custom_emoji_id="6032594876506312598"),
                    InlineKeyboardButton(text="Бонус", callback_data=f"open:bonus", icon_custom_emoji_id="6032644646587338669")
                ],           
                [
                    InlineKeyboardButton(text="Задания", callback_data=f"open:tasks", icon_custom_emoji_id="5924720918826848520")
                ],
                [
                    InlineKeyboardButton(text="Статистика", callback_data=f"open:stats", icon_custom_emoji_id="5938539885907415367")
                ],
                [
                    InlineKeyboardButton(text="Профиль", callback_data=f"open:profile", icon_custom_emoji_id="6035084557378654059")
                ],
                [
                    InlineKeyboardButton(text="Админ Панель", callback_data=f"admin:main", icon_custom_emoji_id="5940433880585605708")    
                ]
            ]
            return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
        else:
            inline_kb_list = [
                [
                    InlineKeyboardButton(text="Рефералы", callback_data=f"open:refs", icon_custom_emoji_id="6032594876506312598"),
                    InlineKeyboardButton(text="Бонус", callback_data=f"open:bonus", icon_custom_emoji_id="6032644646587338669")
                ],         
                [
                    InlineKeyboardButton(text="Задания", callback_data=f"open:tasks", icon_custom_emoji_id="5924720918826848520")
                ],
                [
                    InlineKeyboardButton(text="Статистика", callback_data=f"open:stats", icon_custom_emoji_id="5938539885907415367")
                ],
                [
                    InlineKeyboardButton(text="Профиль", callback_data=f"open:profile", icon_custom_emoji_id="6035084557378654059")
                ]
            ]
            return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
        
    async def statsKb():
        inline_kb_list = [
           [
               InlineKeyboardButton(text="Канал", url=f"t.me/meimunteamchannel", icon_custom_emoji_id="5323773875069135560"),
               InlineKeyboardButton(text="Выплаты", url=f"t.me/meimunusdtpayots", icon_custom_emoji_id="5987880246865565644")
           ],
           [
               InlineKeyboardButton(text="Отзывы", url=f"t.me/MeimunReviews", icon_custom_emoji_id="6028530359975548369"),
               InlineKeyboardButton(text="Чат", url=f"t.me/MeimunChat", icon_custom_emoji_id="5994297722574737553")
           ],
           [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="open:main", icon_custom_emoji_id="5960671702059848143")
           ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def getSupport():
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Поддержка", url=f"{await AsyncConfigManager.get("support", "support_account")}", icon_custom_emoji_id="6030400221232501136")]])
    async def backToMainKb(cb):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data=cb, icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def backInWithdrawKb(cb):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Повторить попытку", callback_data=cb)                
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="open:withdraw", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def getProfilePageKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Вывод", callback_data="open:withdraw", icon_custom_emoji_id="5987880246865565644"),
                InlineKeyboardButton(text="Промокод", callback_data="open:promo", icon_custom_emoji_id="6032644646587338669")
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="open:main", icon_custom_emoji_id="5960671702059848143")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def nextTask():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Следующее задание", callback_data="open:tasks", icon_custom_emoji_id="5825794181183836432"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="open:main", icon_custom_emoji_id="5960671702059848143")
            ]

        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

    async def acceptTask(link, taskId):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Перейти", url=link, icon_custom_emoji_id="6028171274939797252"),
                InlineKeyboardButton(text="Проверить", callback_data=f"open:task:accept_{taskId}", icon_custom_emoji_id="5825794181183836432"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="open:main", icon_custom_emoji_id="5960671702059848143")
            ]

        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def getWithdrawTypesKb():
        inline_kb_list = [
            [
                InlineKeyboardButton(text="CryptoBot", callback_data="open:withdraw:cb", icon_custom_emoji_id="5807465992363710697"),
            ],
            [
                InlineKeyboardButton(text="Вернуться в меню", style="primary", callback_data="open:profile", icon_custom_emoji_id="5960671702059848143")
            ]

        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
    async def checkAndWithdraw(type: str, sum: int):
        inline_kb_list = [
            [
                InlineKeyboardButton(text="Вывод", style="success", callback_data=f"success_wd:{type}:{sum}", icon_custom_emoji_id="5875180111744995604")
            ],
            [
                InlineKeyboardButton(text="Отмена", style="danger", callback_data="open:profile", icon_custom_emoji_id="5960671702059848143")
            ]

        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)
     
