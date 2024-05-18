from httpx import AsyncClient


async def search(keyword: str) -> dict:
    async with AsyncClient(verify=False) as client:
        response = await client.get(
            f"https://myanimelist.net/search/prefix.json?type=anime&keyword={keyword}"
        )
        return response.json()
