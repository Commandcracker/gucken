from ..networking import AsyncClient
from .common import DirectLink, Hoster
from ..utils import json_loads


class LoadXHoster(Hoster):
    async def get_direct_link(self) -> DirectLink:
        async with AsyncClient(verify=False) as client:
            response = await client.head(self.url)
            id_hash = response.url.path.split("/")[2]
            host = response.url.host
            response = await client.post(
                f"https://{host}/player/index.php?data={id_hash}&do=getVideo",
               headers={"X-Requested-With": "XMLHttpRequest"}
            )
            data = json_loads(response.text)
            return DirectLink(url=data.get("videoSource"), force_hls=True)
