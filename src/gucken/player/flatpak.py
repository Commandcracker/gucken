from dataclasses import dataclass

from .mpv import MPVPlayer, CelluloidPlayer
from .vlc import VLCPlayer


@dataclass
class FlatpakMPVPlayer(MPVPlayer):
    executable: str = None

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
            headers
        )
        uf_args.pop(0)
        return ["flatpak", "run", "io.mpv.Mpv"] + uf_args


@dataclass
class FlatpakCelluloidPlayer(CelluloidPlayer):
    executable: str = None

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
            headers
        )
        uf_args.pop(0)
        return ["flatpak", "run", "io.github.celluloid_player.Celluloid"] + uf_args


@dataclass
class FlatpakVLCPlayer(VLCPlayer):
    executable: str = None

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
            headers
        )
        uf_args.pop(0)
        return ["flatpak", "run", "org.videolan.VLC"] + uf_args
