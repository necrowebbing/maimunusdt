from sources.utils.configmanager import AsyncConfigManager
import requests

async def create_paste_simple(text, title, private=True):
    url = "https://pastebin.com/api/api_post.php"
    APIKEY = await AsyncConfigManager.get("other", "pastebin_api")
    data = {
        'api_dev_key': APIKEY,
        'api_option': 'paste',
        'api_paste_code': text,
        'api_paste_private': 1 if private else 0,  # 0=публичная, 1=только по ссылке
        'api_paste_name': title,
        'api_paste_format': 'text',
        'api_paste_expire_date': '1D'
    }
    
    response = requests.post(url, data=data)
    return response.text