from dataclasses import dataclass
from os import getenv
from os import name as os_name
from os.path import join
from shutil import which

from .common import Player, dict_to_string


@dataclass
class MPVPlayer(Player):
    supports_headers: bool = True

    @staticmethod
    def detect_executable() -> str:
        if os_name == "nt" and which("mpv.exe"):
            return "mpv.exe"
        if which("mpv"):
            return "mpv"

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
            args.append("--fullscreen")
        if title:
            args.append(f"--force-media-title={title}")
        if headers:
            args.append(f"--http-header-fields={dict_to_string(headers)}")
        return args


@dataclass
class MPVNETPlayer(MPVPlayer):
    @staticmethod
    def detect_executable() -> str:
        if os_name == "nt":
            if which("mpvnet.exe"):
                return "mpvnet.exe"
            if getenv("LOCALAPPDATA"):
                mpvnet = join(
                    getenv("LOCALAPPDATA"), "Programs", "mpv.net", "mpvnet.exe"
                )
                if which(mpvnet):
                    return mpvnet

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        return super().play(
            url, title, full_screen, headers, override_executable or self.executable
        ) + ["--process-instance=multi"]


class CelluloidPlayer(MPVPlayer):
    @staticmethod
    def detect_executable() -> str:
        if os_name == "posix":
            if which("celluloid"):
                return "celluloid"

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        uf_args = super().play(
            url, title, full_screen, headers, override_executable or self.executable
        )
        args = [uf_args[0], uf_args[1]]
        uf_args.pop(0)
        uf_args.pop(0)
        for arg in uf_args:
            args.append(f"--mpv-{arg.lstrip('-')}")
        return args + ["--new-window"]
