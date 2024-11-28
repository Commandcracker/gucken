from base64 import b64decode
from re import compile as re_compile

from ..networking import AsyncClient
from .common import DirectLink, Hoster


REDIRECT_PATTERN = re_compile("https?://[^\s'\"<>]+")
EXTRACT_VEO_HLS_PATTERN = re_compile(r"'hls': '(?P<hls>.*)'")


class VOEHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url)
            match = REDIRECT_PATTERN.search(response.text)
            link = match.group()

            response2 = await client.get(link)
            match2 = EXTRACT_VEO_HLS_PATTERN.search(response2.text)
            link2 = match2.group("hls")

            return DirectLink(b64decode(link2).decode())
