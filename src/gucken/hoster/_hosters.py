from textual._two_way_dict import TwoWayDict

from .doodstream import DoodstreamHoster
from .streamtape import StreamtapeHoster
from .veo import VOEHoster
from .vidoza import VidozaHoster
from .filemoon import FilemoonHoster
from .luluvdo import LuluvdoHoster
from .speedfiles import SpeedFilesHoster
from .vidmoly import VidmolyHoster

hoster = TwoWayDict(
    {
        "DS": DoodstreamHoster,
        "ST": StreamtapeHoster,
        "VEO": VOEHoster,
        "VZ": VidozaHoster,
        "FM": FilemoonHoster,
        "LU": LuluvdoHoster,
        "SF": SpeedFilesHoster,
        "VM": VidmolyHoster
    }
)
