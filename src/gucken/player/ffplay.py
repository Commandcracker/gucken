from dataclasses import dataclass
from shutil import which

from .common import Player, dict_to_string


@dataclass
class FFPlayPlayer(Player):
    supports_headers: bool = True

    @staticmethod
    def detect_executable() -> str:
        if which("ffplay"):
            return "ffplay"

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        args = [override_executable or self.detect_executable(), url]
        if title:
            args.append("-window_title")
            args.append(title)
        if headers:
            args.append(f"-headers={dict_to_string(headers)}")
        return args
