import sys
from os import name as os_name, getenv
from os.path import join
from shutil import which
from subprocess import Popen, DEVNULL
from typing import Union

from .player.android import AndroidChoosePlayer, AndroidMPVPlayer, AndroidVLCPlayer
from .player.common import Player
from .player.ffplay import FFPlayPlayer
from .player.mpv import MPVPlayer, MPVNETPlayer, CelluloidPlayer
from .player.vlc import VLCPlayer
from .player.wmplayer import WMPlayer
from .player.flatpak import FlatpakMPVPlayer, FlatpakVLCPlayer, FlatpakCelluloidPlayer


is_android = hasattr(sys, "getandroidapilevel")


def detect_player() -> Union[Player, None]:
    if is_android:
        # TODO: Detect right
        return AndroidMPVPlayer()
        # return AndroidVLCPlayer()
        # return AndroidChoosePlayer()
        # return None

    if os_name == "nt":
        if which("mpv.exe"):
            return MPVPlayer("mpv.exe")
    elif which("mpv"):
        return MPVPlayer()

    if os_name == "nt":
        if which("mpvnet.exe"):
            return MPVNETPlayer()
        if getenv("LOCALAPPDATA"):
            mpvnet = join(getenv("LOCALAPPDATA"), "Programs", "mpv.net", "mpvnet.exe")
            if which(mpvnet):
                return MPVNETPlayer(mpvnet)

    if os_name == "posix":
        if which("celluloid"):
            return CelluloidPlayer()

    if which("vlc"):
        return VLCPlayer()

    if os_name == "posix":
        # TODO: fix this will slow down
        if which("flatpak"):
            p = Popen(["flatpak", "info", "io.mpv.Mpv"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)
            if p.wait() == 0:
                return FlatpakMPVPlayer()
            p = Popen(["flatpak", "info", "io.github.celluloid_player.Celluloid"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)
            if p.wait() == 0:
                return FlatpakCelluloidPlayer()
            p = Popen(["flatpak", "info", "org.videolan.VLC"], stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)
            if p.wait() == 0:
                return FlatpakVLCPlayer()

    if os_name == "nt":
        vlc = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if which(vlc):
            return VLCPlayer(vlc)

    if which("ffplay"):
        return FFPlayPlayer()

    if os_name == "nt":
        return WMPlayer()

    return None
