from re import compile as re_compile

from ..networking import AsyncClient

from .common import DirectLink, Hoster

VIDMOLY_PATTERN = re_compile("")

# TODO: WIP !!!
class VidmolyHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        return DirectLink("WIP")
