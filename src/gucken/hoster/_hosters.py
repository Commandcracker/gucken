from textual._two_way_dict import TwoWayDict

from .doodstream import DoodstreamHoster
from .streamtape import StreamtapeHoster
from .veo import VOEHoster
from .vidoza import VidozaHoster

hoster = TwoWayDict(
    {
        "DS": DoodstreamHoster,
        "ST": StreamtapeHoster,
        "VEO": VOEHoster,
        "VZ": VidozaHoster,
    }
)
