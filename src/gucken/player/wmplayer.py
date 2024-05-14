from dataclasses import dataclass

from .common import Player


@dataclass
class WMPlayer(Player):
    executable: str = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"

    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        args = [
            override_executable or self.executable,
            url
        ]
        if full_screen:
            args.append("/fullscreen")
        return args
