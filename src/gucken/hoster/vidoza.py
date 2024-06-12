from re import compile as re_compile

from ..networking import AsyncClient

from .common import DirectLink, Hoster

EXTRACT_VIDOZA_HLS_PATTERN = re_compile(
    r"sourcesCode:.*?\[.*?\{.*?src:.*?[\'|\"](?P<mp4>.*?)[\'|\"],"
)


class VidozaHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url)
            match = EXTRACT_VIDOZA_HLS_PATTERN.search(response.text)
            return DirectLink(match.group("mp4"))
