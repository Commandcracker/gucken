import sys
from typing import Union

from .player.android import AndroidChoosePlayer
from .player.common import Player
from .player.ffplay import FFPlayPlayer
from .player.flatpak import FlatpakCelluloidPlayer, FlatpakMPVPlayer, FlatpakVLCPlayer
from .player.mpv import CelluloidPlayer, MPVNETPlayer, MPVPlayer
from .player.vlc import VLCPlayer
from .player.wmplayer import WMPlayer

is_android = hasattr(sys, "getandroidapilevel")


def detect_player() -> Union[Player, None]:
    if is_android:
        return AndroidChoosePlayer()

    prio_list = [
        MPVPlayer,
        MPVNETPlayer,
        CelluloidPlayer,
        VLCPlayer,
        FlatpakMPVPlayer,
        FlatpakCelluloidPlayer,
        FlatpakVLCPlayer,
        FFPlayPlayer,
        WMPlayer,
    ]

    for p in prio_list:
        if p.is_available():
            return p()

    return None
