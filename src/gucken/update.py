from dataclasses import dataclass
from typing import Union

from .networking import AsyncClient
from packaging.version import Version

from . import __version__ as current_version
from .utils import json_loads

PACKAGE_NAME = "gucken"


@dataclass
class UpdateResult:
    current: str
    latest: str


async def get_latest_version():
    async with AsyncClient() as client:
        response = await client.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json")
        return json_loads(response.content).get("info").get("version")


async def check() -> Union[UpdateResult, None]:
    latest_version = await get_latest_version()
    if Version(latest_version) > Version(current_version):
        return UpdateResult(current_version, latest_version)
    return None


def main():
    from asyncio import run

    print(run(check()))


if __name__ == "__main__":
    main()
