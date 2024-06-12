from base64 import b64decode
from re import compile as re_compile

from ..networking import AsyncClient
from .common import DirectLink, Hoster

EXTRACT_VEO_HLS_PATTERN = re_compile(r"'hls': '(?P<hls>.*)'")


class VOEHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url)
            match = EXTRACT_VEO_HLS_PATTERN.search(response.text)
            link = match.group("hls")
            return DirectLink(b64decode(link).decode())
