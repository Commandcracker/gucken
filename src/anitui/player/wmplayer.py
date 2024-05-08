from .common import Player


class WMPlayer(Player):
    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        return [
            override_executable or r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe",
            url,
            "/fullscreen" if full_screen else "",
        ]
