from re import compile as re_compile

from httpx import AsyncClient

from .common import DirectLink, Hoster

STREAMTAPE_PATTERN = re_compile(r"botlink(.*?)innerHTML(.*?)\);")
STREAMTAPE_PATTERN_SUBSTRING = re_compile(r"substring\(\d+")
STREAMTAPE_PATTERN_DIGETS = re_compile(r"\d+")


class StreamtapeHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        # TODO: Error checking
        async with AsyncClient(verify=False) as client:
            response = await client.get(self.url, follow_redirects=True)
            # TODO: Save html and error in order to investigate
            # with open("out.txt", "wb") as f:
            #    f.write(response.text.encode('utf-8'))
            video_src = STREAMTAPE_PATTERN.search(response.text)
            j1 = "".join(video_src.groups())
            u1 = j1.split(" ")[2][1:-2]
            u2 = j1[j1.index("('") + 2 : j1.rfind("')")]

            matches = STREAMTAPE_PATTERN_SUBSTRING.findall(j1)
            for match in matches:
                sub = STREAMTAPE_PATTERN_DIGETS.search(match).group(0)
                u2 = u2[int(sub) :]

            return DirectLink(f"https:{u1}{u2}")
