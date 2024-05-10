from .common import Player, dict_to_string


class MPVPlayer(Player):
    supports_headers = True

    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        args = [
            override_executable or "mpv",
            url
        ]
        if full_screen:
            args.append("--fullscreen")
        if title:
            args.append(f"--force-media-title={title}")
        if headers:
            args.append(f"--http-header-fields={dict_to_string(headers)}")
        return args
