from re import compile as re_compile

from ..networking import AsyncClient
from .common import DirectLink, Hoster

STREAMTAPE_PATTERN = re_compile(r"'botlink.*innerHTML.*?'(?P<s1>.*)'.*?\+.*?'(?P<s2>.*)'")


class StreamtapeHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        # TODO: Error checking
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url)

            # TODO: Save html and error in order to investigate
            # with open("out.txt", "wb") as f:
            #    f.write(response.text.encode('utf-8'))

            match = STREAMTAPE_PATTERN.search(response.text)
            return DirectLink(f"https:{match.group('s1')}{match.group('s2')[4:]}")
