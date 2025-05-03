import sys
from html import unescape
from os import getenv
from os.path import join, dirname
from typing import Union, NamedTuple

from .player.android import AndroidChoosePlayer
from .player.common import Player
from .player.ffplay import FFPlayPlayer
from .player.flatpak import FlatpakCelluloidPlayer, FlatpakMPVPlayer, FlatpakVLCPlayer
from .player.mpv import CelluloidPlayer, MPVNETPlayer, MPVPlayer
from .player.vlc import VLCPlayer
from .player.wmplayer import WMPlayer

is_android = hasattr(sys, "getandroidapilevel")
is_windows = sys.platform.startswith("win")
is_linux = sys.platform.startswith("linux")
is_mac_os = sys.platform.startswith("darwin")
is_bsd = "freebsd" in sys.platform or sys.platform.startswith("dragonfly")

try:
    from orjson import loads as json_loads
except ImportError:
    from json import loads as json_loads


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


class VLCPaths(NamedTuple):
    vlc_intf_path: str
    vlc_intf_user_path: str
    vlc_module_path: str


def get_vlc_intf_user_path(player_path: str) -> VLCPaths:
    if is_linux:
        if 'snap' in player_path:
            vlc_intf_path = '/snap/vlc/current/usr/lib/vlc/lua/intf/'
            vlc_intf_user_path = join(getenv('HOME', '.'), "snap/vlc/current/.local/share/vlc/lua/intf/")
        else:
            vlc_intf_path = "/usr/lib/vlc/lua/intf/"
            vlc_intf_user_path = join(getenv('HOME', '.'), ".local/share/vlc/lua/intf/")
    elif is_mac_os:
        vlc_intf_path = "/Applications/VLC.app/Contents/MacOS/share/lua/intf/"
        vlc_intf_user_path = join(
            getenv('HOME', '.'), "Library/Application Support/org.videolan.vlc/lua/intf/")
    elif is_bsd:
        # *BSD ports/pkgs install to /usr/local by default.
        # This should also work for all the other BSDs, such as OpenBSD or DragonFly.
        vlc_intf_path = "/usr/local/lib/vlc/lua/intf/"
        vlc_intf_user_path = join(getenv('HOME', '.'), ".local/share/vlc/lua/intf/")
    elif "vlcportable.exe" in player_path.lower():
        vlc_intf_path = dirname(player_path).replace("\\", "/") + "/App/vlc/lua/intf/"
        vlc_intf_user_path = vlc_intf_path
    else:
        vlc_intf_path = dirname(player_path).replace("\\", "/") + "/lua/intf/"
        vlc_intf_user_path = join(getenv('APPDATA', '.'), "VLC\\lua\\intf\\")

    vlc_module_path = vlc_intf_path + "modules/?.luac"

    return VLCPaths(
        vlc_intf_path=vlc_intf_path,
        vlc_intf_user_path=vlc_intf_user_path,
        vlc_module_path=vlc_module_path
    )


def set_default_vlc_interface_cfg(key: str, value: any) -> str:
    return f'config["{key}"] = config["{key}"] or ' + str(value) or "nil"


def fully_unescape(s: str) -> str:
    """
    Aniworld and SerienStream have many broken/escaped html entities.
    This function will unescape all of them!
    """
    while True:
        prev = s
        s = unescape(s)
        if s == prev:
            break
    return s
