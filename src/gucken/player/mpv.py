from .common import Player, dict_to_string


class MPVPlayer(Player):
    executable = "mpv"
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
            override_executable or self.executable,
            url
        ]
        if full_screen:
            args.append("--fullscreen")
        if title:
            args.append(f"--force-media-title={title}")
        if headers:
            args.append(f"--http-header-fields={dict_to_string(headers)}")
        return args


class MPV_NETPlayer(MPVPlayer):
    executable = "mpvnet"

    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        return super().play(
            url,
            title,
            full_screen,
            headers,
            override_executable or self.executable
        ) + ["--process-instance=multi"]


class CelluloidPlayer(MPVPlayer):
    executable = "celluloid"

    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        uf_args = super().play(
            url,
            title,
            full_screen,
            headers,
            override_executable or self.executable
        )
        args = []
        for arg in uf_args:
            args.append(f"--mpv-{arg.lstrip('-')}")
        return args + ["--new-window"]
