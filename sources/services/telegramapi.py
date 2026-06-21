from sources.utils.configmanager import AsyncConfigManager
import aiohttp

async def SendLogMessage(text: str):
    BOT_TOKEN = "8843613001:AAFhrYbF1vEjc1-KaR-2myX1ijlA_dJTsP4"

    chat_id = await AsyncConfigManager.get(
        "admins",
        "admins_chat"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    connector = aiohttp.TCPConnector(ssl=False)

    try:
        async with aiohttp.ClientSession(
            connector=connector
        ) as session:

            async with session.post(
                url,
                data=payload
            ) as resp:

                result = await resp.json()

                print(result)

                if not resp.ok:
                    raise Exception(
                        f"Telegram error: {result}"
                    )

                return result

    except Exception as e:
        print(f"[TELEGRAM LOG ERROR] {e}")
        return None