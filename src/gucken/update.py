from dataclasses import dataclass
from typing import Union

from httpx import AsyncClient
from packaging.version import Version

from . import __version__ as current_version

PACKAGE_NAME = "gucken"


@dataclass
class UpdateResult:
    current: str
    latest: str


async def get_latest_version():
    async with AsyncClient(verify=False) as client:
        response = await client.get(f"https://pypi.org/pypi/{PACKAGE_NAME}/json")
        return response.json().get("info").get("version")


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
