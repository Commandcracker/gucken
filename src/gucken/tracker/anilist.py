from ..networking import AsyncClient
from ..utils import json_loads

SEARCH_QUERY = """
query ($id: Int, $page: Int, $perPage: Int, $search: String) {
  Page (page: $page, perPage: $perPage) {
    pageInfo {
      total
      currentPage
      lastPage
      hasNextPage
      perPage
    }
    media (id: $id, search: $search) {
      id
      title {
        romaji
        english
        native
      }
    }
  }
}
"""


async def search(keyword: str) -> dict:
    async with AsyncClient() as client:
        response = await client.post(
            "https://graphql.anilist.co",
            headers={"Content-Type": "application/json"},
            json={"query": SEARCH_QUERY, "variables": {"search": keyword}},
        )
        return json_loads(response.content)
