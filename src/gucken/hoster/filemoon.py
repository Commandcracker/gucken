from re import compile as re_compile

from .common import DirectLink, Hoster
from ..networking import AsyncClient
from ..packer import unpack

REDIRECT_REGEX = re_compile(r'<iframe *(?:[^>]+ )?src=(?:\'([^\']+)\'|"([^"]+)")[^>]*>')
SCRIPT_REGEX = re_compile(r'(?s)<script\s+[^>]*?data-cfasync=["\']?false["\']?[^>]*>(.+?)</script>')
VIDEO_URL_REGEX = re_compile(r'file:\s*"([^"]+\.m3u8[^"]*)"')

class FilemoonHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url)
            source = response.text

            match = REDIRECT_REGEX.search(source)
            if match:
                redirect_url = match.group(1) or match.group(2)
                response = await client.get(redirect_url, headers={"Sec-Fetch-Dest": "iframe"})
                source = response.text

            for script_match in SCRIPT_REGEX.finditer(source):
                script_content = script_match.group(1).strip()
                if not script_content.startswith("eval("):
                    continue

                unpacked = unpack(script_content)
                if not unpacked:
                    continue

                video_match = VIDEO_URL_REGEX.search(unpacked)
                if video_match:
                    return DirectLink(video_match.group(1))
