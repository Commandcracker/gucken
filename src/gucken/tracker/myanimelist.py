from ..networking import AsyncClient
from ..utils import json_loads


async def search(keyword: str) -> dict:
    async with AsyncClient() as client:
        response = await client.get(
            f"https://myanimelist.net/search/prefix.json?type=anime&keyword={keyword}"
        )
        return json_loads(response.content)
