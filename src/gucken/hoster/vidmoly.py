from dataclasses import dataclass
from re import compile as re_compile

from ..networking import AsyncClient

from .common import DirectLink, Hoster

VIDMOLY_PATTERN = re_compile(r"sources: \[{file:\"(?P<url>.*?)\"}]")


@dataclass
class VidmolyHoster(Hoster):
    requires_headers = True

    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False, auto_referer=False) as client:
            response = await client.get(self.url)
            match = VIDMOLY_PATTERN.search(response.text)
            return DirectLink(
                url=match.group("url"),
                headers={"Referer": "https://vidmoly.to/"}
            )
