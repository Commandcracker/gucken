from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Union

from ..hoster.common import Hoster


class Language(Enum):
    DE = "Deutsch"
    EN = "English"
    EN_DESUB = "English mit deutschen untertitel"
    JP_DESUB = "Japanisch mit deutschen untertitel"
    JP_ENSUB = "Japanisch mit englischen untertitel"


@dataclass
class Episode:
    title: str
    season: int
    episode_number: int
    total_episode_number: int
    # language: list[Language]
    # hoster: set[Hoster]
    # title_en: str
    # title_de: Union[str, None]
    # language: set[Language]
    # hoster: set[Hoster]
    # number: int

    available_language: list[Language]
    available_hoster: list[Hoster]

    @abstractmethod
    async def process_hoster(self) -> dict[Language, list[Hoster]]:
        raise NotImplementedError


@dataclass
class Series:
    name: str
    episodes: list[Episode]
    cover: str

    # description: str

    @abstractmethod
    def to_markdown(self) -> str:
        raise NotImplementedError


@dataclass
class SearchResult:
    name: str
    description: str = None
    cover: str = None
    provider_name: str = None

    @abstractmethod
    async def get_series(self) -> Series:
        raise NotImplementedError

    @property
    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    def __hash__(self):
        return hash(self.provider_name + self.name + self.description)


class Provider(ABC):

    @staticmethod
    @property
    @abstractmethod
    def host() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def search(keyword: str) -> Union[list[SearchResult]]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def get_series(search_result: SearchResult) -> Series:
        raise NotImplementedError
