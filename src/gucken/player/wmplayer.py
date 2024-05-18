from os import name as os_name
from shutil import which

from .common import Player


class WMPlayer(Player):
    @staticmethod
    def detect_executable() -> str:
        if os_name == "nt":
            path = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"
            if which(path):
                return path

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        args = [override_executable or self.executable, url]
        if full_screen:
            args.append("/fullscreen")
        return args
