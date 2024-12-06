from re import compile as re_compile
from base64 import b64decode

from ..networking import AsyncClient

from .common import DirectLink, Hoster

SPEEDFILES_PATTERN = re_compile("var _0x5opu234 = \"(?P<stuff>.*?)\";")

class SpeedFilesHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url)
            match = SPEEDFILES_PATTERN.search(response.text)
            stuff = match.group("stuff")
            stuff = b64decode(stuff).decode()
            stuff = stuff.swapcase()
            stuff = ''.join(reversed(stuff))
            stuff = b64decode(stuff).decode()
            stuff = ''.join(reversed(stuff))
            stuff2 = ""
            for i in range(0, len(stuff), 2):
                stuff2 += chr(int(stuff[i:i + 2], 16))
            stuff3 = ""
            for char in stuff2:
                stuff3 += chr(ord(char) - 3)
            stuff3 = stuff3.swapcase()
            stuff3 = ''.join(reversed(stuff3))
            stuff3 = b64decode(stuff3).decode()
            return DirectLink(stuff3)
