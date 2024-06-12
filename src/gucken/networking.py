from enum import Enum
from .utils import json_loads
from pathlib import Path
from random import choice
from urllib.parse import urlparse

from httpx import AsyncClient as HttpxAsyncClient, Response, AsyncBaseTransport

from rich import print
from asyncio import run


# https://www.useragents.me/
# https://github.com/microlinkhq/top-user-agents/blob/master/src/index.json
# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils/networking.py
# TODO: generate and dict into ios android mac win etc
user_agents_path = Path(__file__).parent.joinpath("resources", "user_agents.json")
with open(user_agents_path, "r") as f:
    user_agents_raw = f.read()
user_agents = json_loads(user_agents_raw)


class AsyncHTTPSRedirectTransport(AsyncBaseTransport):
    async def handle_async_request(self, request) -> Response:
        url = request.url.copy_with(scheme="https")
        return Response(303, headers={"Location": str(url)})


class AcceptLanguage(Enum):
    EN = 0
    DE = 1


class AsyncClient(HttpxAsyncClient):
    def __init__(
            self,
            *args,
            http2: bool = True,
            follow_redirects: bool = True,
            auto_referer: bool = True,
            https_only: bool = True,
            accept_language: AcceptLanguage = AcceptLanguage.EN,
            **kwargs
    ) -> None:
        # verify=False
        self.auto_referer = auto_referer
        kwargs["http2"] = http2
        kwargs["follow_redirects"] = follow_redirects

        # aiodns / dnspython[doh]
        # socksio - SOCKS proxy support. (Optional, with httpx[socks])

        user_agent = choice(user_agents)
        headers = {
            # Add others
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            # "br" = "brotli" -> httpx[brotli]
            # "zstd" -> httpx[zstd] wait for next release https://github.com/encode/httpx/pull/3139
            # "Accept-Encoding": "gzip, deflate, br", httpx is covering this
            # "Accept-Language": "en-us,en;q=0.5",  see below
            # "Host": "xxx", httpx is covering this
            # "Sec-Ch-Ua-Platform": "macOS",  # only on mac
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",  # Not on iphone
            "Upgrade-Insecure-Requests": "1",  # Not on iphone
            "User-Agent": user_agent
            # "X-Amzn-Trace-Id": "Root=1-xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx"
            # TODO: More variation
        }

        if accept_language is accept_language.EN:
            headers["Accept-Language"] = "en-us,en;q=0.5"  # "en-US,en;q=0.9", "en-US"
        elif accept_language is accept_language.DE:
            headers["Accept-Language"] = choice([
                "de-DE,de;q=0.9",
                "de",  # found on macos
                "de-DE,de;q=0.9",  # found on ios
                "de-DE,de",
                "de,en-US;q=0.7,en;q=0.3"
            ])
        else:
            raise Exception()

        if kwargs.get("headers") is not None:
            headers = {**kwargs.get("headers"), **headers}
        kwargs["headers"] = headers

        if https_only is True:
            kwargs["mounts"] = {"http://": AsyncHTTPSRedirectTransport()}

        super().__init__(*args, **kwargs)

    async def request(self, *args, **kwargs) -> Response:
        if self.auto_referer is True:
            parsed_url = urlparse(args[1])  # maby use httpx.URL instead ?
            base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
            headers = {"Referer": base_url}
            if kwargs.get("headers") is not None:
                headers = {**kwargs.get("headers"), **headers}
            kwargs["headers"] = headers
        return await super().request(*args, **kwargs)


async def main():
    async with AsyncClient() as client:
        response = await client.get("https://httpbin.org/headers")
        print(json_loads(response.content))
    async with HttpxAsyncClient() as client:
        response = await client.get("https://httpbin.org/headers")
        print(json_loads(response.content))

if __name__ == "__main__":
    run(main())
