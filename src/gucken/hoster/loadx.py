from re import compile as re_compile

from ..networking import AsyncClient

from .common import DirectLink, Hoster

LOADX_PATTERN = re_compile("")

# TODO: WIP !!!
class LoadXHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        # https://github.com/Gujal00/ResolveURL/blob/master/script.module.resolveurl/lib/resolveurl/plugins/loadx.py
        # https://github.com/bytedream/stream-bypass/blob/c4085f9ac83d9313ebc8e9629067c91dc7fbe064/src/lib/match.ts#L122

        return DirectLink("WIP")
