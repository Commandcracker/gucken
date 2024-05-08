from abc import abstractmethod
from dataclasses import dataclass


@dataclass
class Player:
    supports_headers: bool = False

    @abstractmethod
    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        raise NotImplementedError
