from enum import Enum
from random import choice
from urllib.parse import urlparse
from typing import Union

from httpx import AsyncClient as HttpxAsyncClient, Response, AsyncBaseTransport

from rich import print
from asyncio import run


# https://www.useragents.me/
# https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/utils/networking.py
def random_user_agent():
    _USER_AGENT_TPL = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/%s Safari/537.36'
    _CHROME_VERSIONS = (
        '90.0.4430.212',
        '90.0.4430.24',
        '90.0.4430.70',
        '90.0.4430.72',
        '90.0.4430.85',
        '90.0.4430.93',
        '91.0.4472.101',
        '91.0.4472.106',
        '91.0.4472.114',
        '91.0.4472.124',
        '91.0.4472.164',
        '91.0.4472.19',
        '91.0.4472.77',
        '92.0.4515.107',
        '92.0.4515.115',
        '92.0.4515.131',
        '92.0.4515.159',
        '92.0.4515.43',
        '93.0.4556.0',
        '93.0.4577.15',
        '93.0.4577.63',
        '93.0.4577.82',
        '94.0.4606.41',
        '94.0.4606.54',
        '94.0.4606.61',
        '94.0.4606.71',
        '94.0.4606.81',
        '94.0.4606.85',
        '95.0.4638.17',
        '95.0.4638.50',
        '95.0.4638.54',
        '95.0.4638.69',
        '95.0.4638.74',
        '96.0.4664.18',
        '96.0.4664.45',
        '96.0.4664.55',
        '96.0.4664.93',
        '97.0.4692.20',
    )
    return _USER_AGENT_TPL % choice(_CHROME_VERSIONS)

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
            accept_language: Union[AcceptLanguage, None] = AcceptLanguage.EN,
            **kwargs
    ) -> None:
        # verify=False
        self.auto_referer = auto_referer
        kwargs["http2"] = http2
        kwargs["follow_redirects"] = follow_redirects

        # aiodns / dnspython[doh]
        # socksio - SOCKS proxy support. (Optional, with httpx[socks])

        user_agent = random_user_agent()
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

        if accept_language is AcceptLanguage.EN:
            headers["Accept-Language"] = "en-us,en;q=0.5"  # "en-US,en;q=0.9", "en-US"
        elif accept_language is AcceptLanguage.DE:
            headers["Accept-Language"] = choice([
                "de-DE,de;q=0.9",
                "de",  # found on macos
                "de-DE,de;q=0.9",  # found on ios
                "de-DE,de",
                "de,en-US;q=0.7,en;q=0.3"
            ])

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
    from .utils import json_loads
    async with AsyncClient() as client:
        response = await client.get("https://httpbin.org/headers")
        print(json_loads(response.content))
    async with HttpxAsyncClient() as client:
        response = await client.get("https://httpbin.org/headers")
        print(json_loads(response.content))

if __name__ == "__main__":
    run(main())
