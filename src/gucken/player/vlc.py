from os import name as os_name
from shutil import which

from .common import Player


class VLCPlayer(Player):

    @staticmethod
    def detect_executable() -> str:
        if which("vlc"):
            return "vlc"
        if os_name == "nt":
            path_64bit = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
            if which(path_64bit):
                return path_64bit
            path_32bit = r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"
            if which(path_32bit):
                return path_32bit

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
            # Hehe
            if headers.get("Referer"):
                args.append(f"--http-referrer={headers.get('Referer')}")
            if headers.get("referer"):
                args.append(f"--http-referrer={headers.get('referer')}")
            if headers.get("User-Agent"):
                args.append(f"--http-user-agent={headers.get('User-Agent')}")
            if headers.get("user-agent"):
                args.append(f"--http-user-agent={headers.get('user-agent')}")
            if headers.get("User-agent"):
                args.append(f"--http-user-agent={headers.get('User-agent')}")
            if headers.get("user-Agent"):
                args.append(f"--http-user-agent={headers.get('user-Agent')}")
        return args
