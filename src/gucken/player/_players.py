import sys
from os import name as os_name

from .android import AndroidChoosePlayer, AndroidMPVPlayer, AndroidVLCPlayer
from .ffplay import FFPlayPlayer
from .flatpak import FlatpakCelluloidPlayer, FlatpakMPVPlayer, FlatpakVLCPlayer
from .mpv import CelluloidPlayer, MPVNETPlayer, MPVPlayer
from .vlc import VLCPlayer
from .wmplayer import WMPlayer

is_android = hasattr(sys, "getandroidapilevel")


def get_players():
    if is_android:
        return [AndroidMPVPlayer, AndroidVLCPlayer, AndroidChoosePlayer]
    _all = [MPVPlayer, VLCPlayer, FFPlayPlayer]

    if os_name == "nt":
        return _all + [MPVNETPlayer, WMPlayer]

    if os_name == "posix":
        return _all + [
            CelluloidPlayer,
            FlatpakMPVPlayer,
            FlatpakCelluloidPlayer,
            FlatpakVLCPlayer,
        ]

    return _all


available_players = get_players()

available_players_keys = []
for p in available_players:
    available_players_keys.append(p.__name__)

all_players = [
    AndroidChoosePlayer,
    AndroidMPVPlayer,
    AndroidVLCPlayer,
    FFPlayPlayer,
    MPVPlayer,
    MPVNETPlayer,
    CelluloidPlayer,
    VLCPlayer,
    WMPlayer,
    FlatpakMPVPlayer,
    FlatpakVLCPlayer,
    FlatpakCelluloidPlayer,
]

all_players_keys = []
for p in all_players:
    all_players_keys.append(p.__name__)

player_map = {}
for p in all_players:
    player_map[p.__name__] = p
