from abc import abstractmethod
from dataclasses import dataclass, field


def dict_to_string(dictionary):
    return ','.join([f"{key}: {value}" for key, value in dictionary.items()])


@dataclass
class Player:
    executable: str = field(default=None, init=False)
    supports_headers: bool = field(default=False, init=True)

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
