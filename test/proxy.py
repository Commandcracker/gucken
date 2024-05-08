from asyncio import run
from re import compile as re_compile
from httpx import AsyncClient

EXTRACT_VIDOZA_HLS_PATTERN = re_compile(r"sourcesCode:.*?\[.*?\{.*?src:.*?[\'|\"](?P<hls>.*?)[\'|\"],")


async def main():
    # require httpx[socks]
    async with AsyncClient(verify=False, proxy="socks5://127.0.0.1:9050") as client:
        response = await client.get("https://aniworld.to/redirect/2460187", follow_redirects=True)
        print(response.text)
        match_hls = EXTRACT_VIDOZA_HLS_PATTERN.search(response.text)
        print(match_hls.group(1))


run(main())
