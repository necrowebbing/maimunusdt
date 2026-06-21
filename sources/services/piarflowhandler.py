import aiohttp
import json

from sources.utils.configmanager import AsyncConfigManager
from sources.states.icons import icons
from sources.services import telegramapi


BASE_URL = "https://piarflow.ru/v1"


def safe_json_dump(data):
    try:
        return json.dumps(data, indent=4, ensure_ascii=False)
    except Exception:
        return str(data)


async def safe_response_json(response):
    try:
        return await response.json()
    except Exception:
        try:
            text = await response.text()
            return {"raw": text}
        except Exception:
            return {"error": "invalid response"}


async def GetSponsors(user_id: int, chat_id: int) -> list:
    headers = {
        "Authorization": f"Bearer {await AsyncConfigManager.get('sponsors', 'piar_flow_api')}",
        "Content-Type": "application/json"
    }

    payload = {
        "user_id": user_id,
        "chat_id": chat_id,
        "max_sponsors": 5
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/sponsors", headers=headers, json=payload) as response:

                resp_json = await safe_response_json(response)

                # SAFE LOG (никогда не падает из-за HTML)
                await telegramapi.SendLogMessage(
                    text=(
                        f"{icons.get('download')} <b>PiarFlow Log</b>\n"
                        f"{icons.get('link')} <b>POST:</b> /sponsors\n"
                        f"{icons.get('profile')} <b>User:</b> <code>{user_id}</code>\n"
                        f"{icons.get('chat_link')} <b>Chat:</b> <code>{chat_id}</code>\n"
                        f"{icons.get('warning')} <b>Status:</b> <code>{response.status}</code>\n"
                        f"{icons.get('code')} <b>Response:</b>\n"
                        f"<pre>{safe_json_dump(resp_json)}</pre>"
                    )
                )

                # API DOWN / NOT FOUND
                if response.status == 404:
                    return ["all_ok"]

                if response.status != 200:
                    return ["error"]

                if isinstance(resp_json, dict) and resp_json.get("status") != "ok":
                    return ["error"]

                sponsors_list = resp_json.get("sponsors", []) if isinstance(resp_json, dict) else []

                if not sponsors_list:
                    return ["all_ok"]

                links = []
                for sponsor in sponsors_list:
                    if not isinstance(sponsor, dict):
                        continue

                    if sponsor.get("status") == "unsubscribed":
                        link = sponsor.get("link")
                        if isinstance(link, str) and link.startswith("http"):
                            links.append(link)

                if not links:
                    return ["all_ok"]

                return ["existed", *links]

    except Exception as ex:
        print(f"[PIAR FLOW ERROR] GetSponsors: {ex}")
        return ["error"]


async def CheckSubsOnSponsors(user_id: int, sponsors_list: list):
    headers = {
        "Authorization": f"Bearer {await AsyncConfigManager.get('sponsors', 'piar_flow_api')}",
        "Content-Type": "application/json"
    }

    clean_links = [
        link for link in sponsors_list
        if isinstance(link, str) and link.startswith("http")
    ]

    if not clean_links:
        return ["all_ok"]

    payload = {
        "user_id": user_id,
        "links": clean_links
    }

    print(f"[PIAR FLOW] Checking links: {clean_links}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/sponsors/check", headers=headers, json=payload) as response:

                resp_json = await safe_response_json(response)

                await telegramapi.SendLogMessage(
                    text=(
                        f"{icons.get('download')} <b>PiarFlow Log</b>\n"
                        f"{icons.get('link')} <b>POST:</b> /sponsors/check\n"
                        f"{icons.get('profile')} <b>User:</b> <code>{user_id}</code>\n"
                        f"{icons.get('warning')} <b>Status:</b> <code>{response.status}</code>\n"
                        f"{icons.get('code')} <b>Response:</b>\n"
                        f"<pre>{safe_json_dump(resp_json)}</pre>"
                    )
                )

                if response.status != 200:
                    return ["error"]

                if isinstance(resp_json, dict) and resp_json.get("status") != "ok":
                    return ["error"]

                sponsors = resp_json.get("sponsors", []) if isinstance(resp_json, dict) else []

                bad = []

                for s in sponsors:
                    if not isinstance(s, dict):
                        continue

                    status = s.get("status")
                    link = s.get("link")

                    if status in ["subscribed", "not_counted"]:
                        continue

                    if isinstance(link, str) and link.startswith("http"):
                        bad.append(link)

                if not bad:
                    return ["all_ok"]

                return ["existed", *bad]

    except Exception as ex:
        print(f"[PIAR FLOW ERROR] CheckSubsOnSponsors: {ex}")
        return ["error"]