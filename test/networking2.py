import asyncio
from json import loads
from pathlib import Path

import aiohttp
from aiohttp.resolver import AsyncResolver
from random import choice
from aiohttp_socks import ProxyConnector

# https://github.com/saghul/aiodns?tab=readme-ov-file#note-for-windows-users
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# https://www.useragents.me/
# https://github.com/microlinkhq/top-user-agents/blob/master/src/index.json
# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils/networking.py
user_agents_json = Path(__file__).parent.joinpath("user_agents.json")
with open(user_agents_json, "r") as f:
    user_agents = f.read()
common_header = loads(user_agents)

# https://github.com/aio-libs/aiohttp/issues/8431


def ClientSession(*args, **kwargs) -> aiohttp.ClientSession:
    resolver = AsyncResolver(nameservers=["1.1.1.1"])
    conn = aiohttp.TCPConnector(resolver=resolver)

    headers = {
        "User-Agent": choice(common_header),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",  # TODO: use de on german sites "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
        "Sec-Fetch-Mode": "navigate",
        "Accept-Encoding": "gzip, deflate, br",
        # TODO: "Referer"
        # TODO: More variation
    }

    return aiohttp.ClientSession(*args, **kwargs, connector=conn, headers=headers)


async def main():
    from rich import print
    async with aiohttp.ClientSession() as session:
        async with session.get("https://httpbin.org/headers", headers={}, proxy="http://proxy.com/") as response:
            print(loads(await response.read())["headers"])
async def main():
    #connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
    async with ClientSession() as session:
        async with session.get("https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/?q=f&ia=web", proxy="http://127.0.0.1:8118") as resp:
            print(resp.status)
asyncio.run(main())
