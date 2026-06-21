import aiofiles
import json
from pathlib import Path

class AsyncConfigManager:
    _file_path = Path("config.json")
    _data = {}

    @classmethod
    async def init(cls):
        """
        Инициализация конфига
        """
        if not cls._file_path.exists():
            await cls.save()
        else:
            await cls.load()

    @classmethod
    async def backup(cls):
        return json.dumps(
            cls._data,
            indent=4,
            ensure_ascii=False
        )

    @classmethod
    async def replace(cls, json_content: str):
        try:
            new_data = json.loads(json_content)
            if not isinstance(new_data, dict):
                raise ValueError(
                    "Корень JSON должен быть объектом"
                )
            cls._data = new_data
            await cls.save()
            return True
        except (json.JSONDecodeError, ValueError) as e:
            return False, str(e)

    @classmethod
    async def load(cls):
        """
        Загрузка JSON
        """
        async with aiofiles.open(
            cls._file_path,
            "r",
            encoding="utf-8"
        ) as f:
            content = await f.read()

            cls._data = (
                json.loads(content)
                if content.strip()
                else {}
            )

    @classmethod
    async def save(cls):
        """
        Сохранение JSON
        """
        async with aiofiles.open(
            cls._file_path,
            "w",
            encoding="utf-8"
        ) as f:
            await f.write(
                json.dumps(
                    cls._data,
                    indent=4,
                    ensure_ascii=False
                )
            )

    @classmethod
    async def get(cls, *keys, default=None):
        """
        Получение значения

        await Config.get("bonuses", "ref_bonus")
        """
        data = cls._data

        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return default

        return data

    @classmethod
    async def set(cls, value, *keys):
        """
        Изменение значения

        await Config.set(
            0.05,
            "bonuses",
            "ref_bonus"
        )
        """
        data = cls._data

        for key in keys[:-1]:
            if key not in data:
                data[key] = {}

            data = data[key]

        data[keys[-1]] = value

        await cls.save()

    @classmethod
    async def delete(cls, *keys):
        """
        Удаление ключа
        """
        data = cls._data

        for key in keys[:-1]:
            data = data.get(key, {})

        if keys[-1] in data:
            del data[keys[-1]]

            await cls.save()

    @classmethod
    async def reload(cls):
        """
        Перезагрузка файла
        """
        await cls.load()

    @classmethod
    async def to_python(cls):
        """
        JSON -> Python config
        """
        lines = []

        def walk(obj, prefix=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_prefix = (
                        f"{prefix}_{k}".upper()
                        if prefix
                        else k.upper()
                    )

                    if isinstance(v, dict):
                        walk(v, new_prefix)
                    else:
                        lines.append(
                            f"{new_prefix} = {repr(v)}"
                        )

        walk(cls._data)

        return "\n".join(lines)