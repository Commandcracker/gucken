from re import compile as re_compile

from httpx import AsyncClient

from .common import DirectLink, Hoster

LULUVODO_PATTERN = re_compile(r'file:\s*"([^"]+)"')

class LuluvdoHoster(Hoster):
    requires_headers = True

    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False, follow_redirects=True, headers={"user-agent": "Mozilla/5.0 (Android 15; Mobile; rv:132.0) Gecko/132.0 Firefox/132.0"}) as client:
            response = await client.get(self.url)
            luluvdo_id = response.url.path.split('/')[-1]
            url = f"https://luluvdo.com/dl?op=embed&file_code={luluvdo_id}"
            response = await client.get(url)
            match = LULUVODO_PATTERN.search(response.text)
            return DirectLink(
                url=match.group(1),
                headers={"user-agent": client.headers["user-agent"]},
            )
