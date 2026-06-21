from pathlib import Path
import aiohttp

async def upload_to_temp_sh(file_path: str | Path) -> str:
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    data = aiohttp.FormData()
    with open(file_path, "rb") as f:
        data.add_field(
            "file",
            f,
            filename=file_path.name,
            content_type="text/csv"
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://temp.sh/upload",
                data=data
            ) as response:
                response.raise_for_status()
                return (await response.text()).strip()