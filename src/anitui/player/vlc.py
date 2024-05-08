from .common import Player


class VLCPlayer(Player):
    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        return [
            override_executable or "vlc",
            url,
            "--no-video-title-show",
            "--fullscreen" if full_screen else "",
            "--play-and-exit",
            f"--input-title-format={title}"
        ]
