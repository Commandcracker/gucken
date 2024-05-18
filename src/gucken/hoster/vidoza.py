from re import compile as re_compile

from httpx import AsyncClient

from .common import DirectLink, Hoster

# TODO: improve all patterns
EXTRACT_VIDOZA_HLS_PATTERN = re_compile(
    r"sourcesCode:.*?\[.*?\{.*?src:.*?[\'|\"](?P<hls>.*?)[\'|\"],"
)


class VidozaHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url, follow_redirects=True)
            match_hls = EXTRACT_VIDOZA_HLS_PATTERN.search(response.text)
            return DirectLink(match_hls.group(1))
