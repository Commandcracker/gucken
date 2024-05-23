from os import name as os_name
from subprocess import DEVNULL, Popen

from .common import Player
from .mpv import CelluloidPlayer, MPVPlayer
from .vlc import VLCPlayer


# This is just that you can check if the player is a Flatpak player
class FlatpakPlayer(Player):
    pass


# TODO: Dont use Popen, it will slow down


class FlatpakMPVPlayer(MPVPlayer, FlatpakPlayer):

    @classmethod
    def is_available(cls) -> bool:
        if os_name == "posix":
            p = Popen(
                ["flatpak", "info", "io.mpv.Mpv"],
                stdout=DEVNULL,
                stderr=DEVNULL,
                stdin=DEVNULL,
            )
            if p.wait() == 0:
                return True

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        uf_args = super().play(url, title, full_screen, headers)
        uf_args.pop(0)
        return ["flatpak", "run", "io.mpv.Mpv"] + uf_args


class FlatpakCelluloidPlayer(CelluloidPlayer, FlatpakPlayer):

    @classmethod
    def is_available(cls) -> bool:
        if os_name == "posix":
            p = Popen(
                ["flatpak", "info", "io.github.celluloid_player.Celluloid"],
                stdout=DEVNULL,
                stderr=DEVNULL,
                stdin=DEVNULL,
            )
            if p.wait() == 0:
                return True

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        uf_args = super().play(url, title, full_screen, headers)
        uf_args.pop(0)
        return ["flatpak", "run", "io.github.celluloid_player.Celluloid"] + uf_args


class FlatpakVLCPlayer(VLCPlayer, FlatpakPlayer):

    @classmethod
    def is_available(cls) -> bool:
        if os_name == "posix":
            p = Popen(
                ["flatpak", "info", "org.videolan.VLC"],
                stdout=DEVNULL,
                stderr=DEVNULL,
                stdin=DEVNULL,
            )
            if p.wait() == 0:
                return True

    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        uf_args = super().play(url, title, full_screen, headers)
        uf_args.pop(0)
        return ["flatpak", "run", "org.videolan.VLC"] + uf_args
