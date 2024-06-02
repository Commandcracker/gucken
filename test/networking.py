import logging
import random
import asyncio
import enum
import socket
from typing import List

from aiohttp.abc import AbstractResolver
from aiohttp.client import ClientSession as CS
from aiohttp.connector import TCPConnector
from aiohttp.resolver import DefaultResolver
import json
from pathlib import Path
from rich import print

# TODO: automatically update
# https://raw.githubusercontent.com/microlinkhq/top-user-agents/master/src/index.json
user_agents_json = Path(__file__).parent.joinpath("user_agents.json")
with open(user_agents_json, "r") as f:
    user_agents = f.read()
common_header = json.loads(user_agents)


def random_user_agent():
    # https://www.useragents.me/
    # https://github.com/microlinkhq/top-user-agents/blob/master/src/index.json
    # https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils/networking.py
    return random.choice(common_header)


std_headers = {
    "User-Agent": random_user_agent(),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-us,en;q=0.5",  # TODO: use de on german sites "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    "Sec-Fetch-Mode": "navigate",
    "Accept-Encoding": "gzip, deflate, br",
    # TODO: "Referer"
    # TODO: More variation
}


# https://github.com/aio-libs/aiohttp/issues/8431
class RecordType(enum.Enum):
    """Record Type"""

    A = 1
    AAAA = 28


class DNSOverHTTPSResolver(AbstractResolver):
    """DNS over HTTPS Resolver"""

    def __init__(
            self,
            *,
            endpoints: List[str],
            json_loads=json.loads,
            resolver_class=None,
    ) -> None:
        self.endpoints = endpoints
        self.json_loads = json_loads
        if resolver_class is None:
            resolver_class = DefaultResolver
        self.resolveer_class = resolver_class

    async def _resolve(self, endpoint: str, host, port, family):
        if family == socket.AF_INET6:
            record_type = RecordType.AAAA
        else:
            record_type = RecordType.A

        headers = {
            "Accept": "application/dns-json"
        }
        params = {
            'name': host,
            'type': record_type.name,
        }

        resolver = self.resolveer_class()
        connector = TCPConnector(resolver=resolver)

        async with CS(connector=connector) as session:
            print("E:", endpoint)
            async with session.get(endpoint, params=params, headers=headers) as resp:
                print("T:", resp.content)
                data = self.json_loads(await resp.text())

        await connector.close()

        if data['Status'] != 0:
            raise OSError("DNS lookup failed")

        return [
            {
                'hostname': host,
                'host': r['data'],
                'port': port,
                'family': family,
                'proto': 0,
                'flags': socket.AI_NUMERICHOST
            } for r in data['Answer']
            if r['type'] in (
                record_type.name,
                record_type.value,
            ) and r['data']
        ]

    async def resolve(self, host, port=0, family=socket.AF_INET):
        tasks = await self._resolve(self.endpoints[0], host, port, family)
        print(tasks)
        return tasks

    async def close(self):
        pass


def ClientSession(*args, **kwargs) -> CS:  # noqa
    """Shortcut of aiohttp.ClientSession and DNSOverHTTPSResolver"""

    endpoints = kwargs.pop(
        'endpoints',
        [
            'https://dns.google.com/resolve',
            'https://cloudflare-dns.com/dns-query',
        ],
    )
    json_loads = kwargs.pop('json_loads', json.loads)
    resolver_class = kwargs.pop('resolver_class', None)
    resolver = DNSOverHTTPSResolver(
        endpoints=endpoints,
        json_loads=json_loads,
        resolver_class=resolver_class,
    )
    connector = TCPConnector(resolver=resolver)

    return CS(*args, **kwargs, connector=connector)


async def main():
    async with ClientSession(endpoints=["https://dns.mullvad.net/dns-query"]) as session:
        async with session.get('https://httpbin.org/headers') as resp:
            data = await resp.text()

    print(data)


logging.basicConfig(level=logging.DEBUG)
asyncio.run(main())
