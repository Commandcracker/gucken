from ..networking import AsyncClient


async def search(keyword: str) -> dict:
    async with AsyncClient() as client:
        response = await client.get(
            f"https://myanimelist.net/search/prefix.json?type=anime&keyword={keyword}"
        )
        return response.json()
