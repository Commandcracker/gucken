from abc import abstractmethod
from dataclasses import dataclass


def dict_to_string(dictionary):
    return ",".join([f"{key}: {value}" for key, value in dictionary.items()])


@dataclass
class Player:
    supports_headers: bool = False

    def __new__(cls, *args, **kwargs):
        c = super().__new__(cls, *args, **kwargs)
        c.executable = cls.detect_executable()
        return c

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        return cls.detect_executable() is not None

    @staticmethod
    @abstractmethod
    def detect_executable() -> str:
        pass

    @abstractmethod
    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        raise NotImplementedError
