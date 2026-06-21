from sources.utils.configmanager import AsyncConfigManager
from sources.states.icons import icons
from sources.services import telegramapi
import aiohttp, json

BASE_URL = "https://tgrass.space"

async def ResetTasks(user_id: int) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Auth": f"{await AsyncConfigManager.get("sponsors", "tgrass_api")}"
    }
    payload = {
        "tg_user_id": user_id
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{BASE_URL}/reset_offers", headers=headers, json=payload) as response:
                await telegramapi.SendLogMessage(
                    text=(
                        f"<b>{icons.get("download")} Tgrass Log</b>\n"
                        f"{icons.get("link")}<b>POST:</b> /reset_offers\n"
                        f"{icons.get("profile")}<b>User:</b> <code>{user_id}</code>\n"
                        f"{icons.get("warning")}<b>Status:</b> <code>{response.status}</code>\n"
                        f"{icons.get("code")}<b>JSON Response:</b>\n"
                        f"<pre>{json.dumps(await response.json(), indent=4, ensure_ascii=False)}</pre>"
                    )
                )
                respjson = await response.json()
                if response.status == 200:
                    return respjson
                else:
                    return {"status": "error"}
    except Exception as ex:
        return {"status": "error"}

async def CheckTask(user_id: int, task_id: int) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Auth": f"{await AsyncConfigManager.get("sponsors", "tgrass_api")}"
    }
    payload = {
        "tg_user_id": user_id,
        "offer_id": task_id
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{BASE_URL}/check", headers=headers, json=payload) as response:
                await telegramapi.SendLogMessage(
                    text=(
                        f"<b>{icons.get("download")} Tgrass Log</b>\n"
                        f"{icons.get("link")}<b>POST:</b> /check\n"
                        f"{icons.get("profile")}<b>User:</b> <code>{user_id}</code>\n"
                        f"{icons.get("chat")}<b>offer_id:</b> <code>{task_id}</code>\n"
                        f"{icons.get("warning")}<b>Status:</b> <code>{response.status}</code>\n"
                        f"{icons.get("code")}<b>JSON Response:</b>\n"
                        f"<pre>{json.dumps(await response.json(), indent=4, ensure_ascii=False)}</pre>"
                    )
                )
                respjson = await response.json()
                if response.status == 200:
                    return respjson
                else:
                    return {"status": "error"}
    except Exception as ex:
        return {"status": "error"}

async def GetTask(user_id: int, is_premium: bool, lang: str) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Auth": f"{await AsyncConfigManager.get("sponsors", "tgrass_api")}"
    }
    payload = {
        "tg_user_id": user_id,
        "is_premium": is_premium,
        "lang": lang,
        "offers_limit": 2
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f"{BASE_URL}/tasks", headers=headers, json=payload) as response:
                await telegramapi.SendLogMessage(
                    text=(
                        f"<b>{icons.get("download")} Tgrass Log</b>\n"
                        f"{icons.get("link")}<b>POST:</b> /tasks\n"
                        f"{icons.get("profile")}<b>User:</b> <code>{user_id}</code>\n"
                        f"{icons.get("chat")}<b>isPremium:</b> <code>{is_premium}</code>\n"
                        f"{icons.get("profile")}<b>lang:</b> <code>{lang}</code>\n"
                        f"{icons.get("warning")}<b>Status:</b> <code>{response.status}</code>\n"
                        f"{icons.get("code")}<b>JSON Response:</b>\n"
                        f"<pre>{json.dumps(await response.json(), indent=4, ensure_ascii=False)}</pre>"
                    )
                )
                if response.status == 200:
                    respjson = await response.json()
                    status = respjson.get("status")
                    if status == "ok":
                        return {"status": "ok"}
                    elif status == "no_offers":
                        return {"status": "no_offers"}
                    elif status == "not_ok":
                        task = respjson.get("offers")[0]
                        task["status"] = "not_ok"
                        return task
                    else:
                        return {"status": "error"}
                else:
                    return {"status": "error"}
    except Exception as ex:
        return {"status": "error", "error": ex}