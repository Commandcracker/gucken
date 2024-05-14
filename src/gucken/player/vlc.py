from dataclasses import dataclass

from .common import Player


@dataclass
class VLCPlayer(Player):
    executable: str = "vlc"

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
