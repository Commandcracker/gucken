from re import compile as re_compile

from ..networking import AsyncClient

from .common import DirectLink, Hoster

FILEMOON_PATTERN = re_compile("")

# TODO: WIP !!!
class FilemoonHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        # See https://github.com/shashstormer/godstream/blob/master/extractors/filemoon.py
        return DirectLink("WIP")
