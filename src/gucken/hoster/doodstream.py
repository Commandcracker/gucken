from dataclasses import dataclass
from random import choices
from re import compile as re_compile
from string import ascii_letters, digits
from time import time

from ..networking import AsyncClient
from .common import DirectLink, Hoster

EXTRACT_DOODSTREAM_HLS_PATTERN = re_compile(r"/pass_md5/[\w-]+/(?P<token>[\w-]+)")


def random_str(length: int = 10) -> str:
    return "".join(choices(ascii_letters + digits, k=length))


def js_date_now() -> int:
    return int(time() * 1000)


@dataclass
class DoodstreamHoster(Hoster):
    requires_headers = True

    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False, auto_referer=True) as client:
            response1 = await client.get(self.url)
            match = EXTRACT_DOODSTREAM_HLS_PATTERN.search(response1.text)

            # Require Referer
            response2 = await client.get(str(response1.url.copy_with(path=match.group())))
            return DirectLink(
                url=f"{response2.text}{random_str()}?token={match.group('token')}&expiry={js_date_now()}",
                headers={"Referer": str(response2.url.copy_with(path="/"))},
            )
