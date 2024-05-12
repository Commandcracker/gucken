from base64 import b64decode
from re import compile as re_compile

from httpx import AsyncClient

from .common import DirectLink, Hoster

EXTRACT_VEO_HLS_PATTERN = re_compile(r"'hls': '(.*?)'")


class VOEHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url, follow_redirects=True)
            match_hls = EXTRACT_VEO_HLS_PATTERN.search(response.text)
            hls_link = match_hls.group(1)
            return DirectLink(b64decode(hls_link).decode())
