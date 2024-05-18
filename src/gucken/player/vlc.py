from os import name as os_name
from shutil import which

from .common import Player


class VLCPlayer(Player):

    @staticmethod
    def detect_executable() -> str:
        if which("vlc"):
            return "vlc"
        if os_name == "nt":
            path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
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
        args = [
            override_executable or self.executable,
            url,
            "--no-video-title-show",
            "--play-and-exit",
        ]
        if full_screen:
            args.append("--fullscreen")
        if title:
            args.append(f"--input-title-format={title}")
        if headers:
            if headers.get("Referer"):
                args.append(f"--http-referrer={headers.get('Referer')}")
            if headers.get("User-Agent"):
                args.append(f"--http-user-agent={headers.get('User-Agent')}")
        return args
