from dataclasses import dataclass
from random import choices
from re import compile as re_compile
from string import ascii_letters, digits
from time import time
from urllib.parse import urlparse

from httpx import AsyncClient

from .common import DirectLink, Hoster

EXTRACT_DOODSTREAM_HLS_PATTERN = re_compile(r"/pass_md5/[\w-]+/[\w-]+")


def random_str(length: int = 10) -> str:
    return "".join(choices(ascii_letters + digits, k=length))


def js_date_now() -> int:
    return int(time() * 1000)


headers = {"Referer": "https://d0000d.com/"}


@dataclass
class DoodstreamHoster(Hoster):
    requires_headers = True

    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.head(self.url)
            if response.has_redirect_location:
                u2 = (
                    urlparse(response.headers.get("Location"))
                    ._replace(netloc="d000d.com")
                    .geturl()
                )
                response = await client.get(u2)

            pass_md5 = EXTRACT_DOODSTREAM_HLS_PATTERN.search(response.text)
            response = await client.get(
                f"https://d0000d.com{pass_md5.group()}",
                headers={"Referer": "https://d0000d.com/"},
            )
            return DirectLink(
                url=f"{response.text}{random_str()}?token={pass_md5.group().split('/')[-1]}&expiry={js_date_now()}",
                headers=headers,
            )
