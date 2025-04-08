from base64 import b64decode
from re import compile as re_compile
from ..utils import json_loads

from ..networking import AsyncClient
from .common import DirectLink, Hoster

REDIRECT_PATTERN = re_compile("https?://[^'\"<>]+")

EXTRACT_VEO_HLS_PATTERN = re_compile(r"'hls': '(?P<hls>.*)'")
HIDDEN_JSON_PATTERN = re_compile(r"var a168c='(?P<hidden_json>[^']+)'")

class VOEHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            redirect_response = await client.get(self.url)
            redirect_match = REDIRECT_PATTERN.search(redirect_response.text)
            redirect_link = redirect_match.group()

            response = await client.get(redirect_link)

            match = HIDDEN_JSON_PATTERN.search(response.text)
            if match:
                hidden_json = b64decode(match.group("hidden_json")).decode()
                hidden_json = hidden_json[::-1]
                hidden_json = json_loads(hidden_json)
                hidden_json = hidden_json["source"]
                return DirectLink(hidden_json)

            hls_match = EXTRACT_VEO_HLS_PATTERN.search(response.text)
            hls_link = hls_match.group("hls")
            hls_link = b64decode(hls_link).decode()
            return DirectLink(
                url=hls_link,
                # Requires "host", "origin" or "referer"
                # can be "bypassed" by http get once for players without headers
                headers = {"Referer": "https://nathanfromsubject.com/"}
            )
