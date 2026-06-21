from typing import List
from aiogram.filters import BaseFilter
from aiogram.types import Message
from sources.utils.configmanager import AsyncConfigManager

class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        admins_list = await AsyncConfigManager.get("admins", "admins_list")
        return message.from_user.id in admins_list
