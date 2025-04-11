from textual._two_way_dict import TwoWayDict

from .loadx import LoadXHoster
from .veo import VOEHoster
from .vidoza import VidozaHoster
from .speedfiles import SpeedFilesHoster
from .doodstream import DoodstreamHoster
from .vidmoly import VidmolyHoster
from .filemoon import FilemoonHoster
from .luluvdo import LuluvdoHoster
from .streamtape import StreamtapeHoster

hoster = TwoWayDict(
    {
        "VEO": VOEHoster,
        "VZ": VidozaHoster,
        "SF": SpeedFilesHoster,
        "DS": DoodstreamHoster,
        "VM": VidmolyHoster,
        "FM": FilemoonHoster,
        "LX": LoadXHoster,
        "LU": LuluvdoHoster,
        "ST": StreamtapeHoster
    }
)
