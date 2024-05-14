from .common import Player, dict_to_string
from dataclasses import dataclass


@dataclass
class MPVPlayer(Player):
    executable: str = "mpv"
    supports_headers: bool = True

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


@dataclass
class MPVNETPlayer(MPVPlayer):
    executable: str = "mpvnet"

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


@dataclass
class CelluloidPlayer(MPVPlayer):
    executable: str = "celluloid"

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
        args = [uf_args[0], uf_args[1]]
        uf_args.pop(0)
        uf_args.pop(0)
        for arg in uf_args:
            args.append(f"--mpv-{arg.lstrip('-')}")
        return args + ["--new-window"]
