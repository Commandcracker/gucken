from .common import Player


# This is just that you can check if the player is an Android player
class AndroidPlayer(Player):
    @classmethod
    def is_available(cls) -> bool:
        return True


class AndroidChoosePlayer(AndroidPlayer):
    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        return [
            "am",
            "start",
            "--user",
            "0",
            "-a" "android.intent.action.VIEW",
            "-d",
            url,
            "-c",
            "android.intent.category.BROWSABLE",
        ]


# http://mpv-android.github.io/mpv-android/intent.html
class AndroidMPVPlayer(AndroidPlayer):
    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        return [
            "am",
            "start",
            "--user",
            "0",
            "-a" "android.intent.action.VIEW",
            "-d",
            url,
            "-n",
            "is.xyz.mpv/.MPVActivity",
        ]


# https://wiki.videolan.org/Android_Player_Intents/
class AndroidVLCPlayer(AndroidPlayer):
    def play(
        self,
        url: str,
        title: str,
        full_screen: bool,
        headers: dict[str, str] = None,
        override_executable: str = None,
    ) -> list[str]:
        args = [
            "am",
            "start",
            "--user",
            "0",
            "-a" "android.intent.action.VIEW",
            "-d",
            url,
            "-n",
            "org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity",
        ]
        if title:
            args.append("-e")
            args.append("title")
            args.append(title)
        return args
