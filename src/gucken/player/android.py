from .common import Player


class AndroidChoosePlayer(Player):
    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        return [
            "am",
            "start",
            "--user",
            "0",
            "-a"
            "android.intent.action.VIEW",
            "-d",
            url,
            "-c",
            "android.intent.category.BROWSABLE"
        ]


# http://mpv-android.github.io/mpv-android/intent.html
class AndroidMPVPlayer(Player):
    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        return [
            "am",
            "start",
            "--user",
            "0",
            "-a"
            "android.intent.action.VIEW",
            "-d",
            url,
            "-n",
            "is.xyz.mpv/.MPVActivity"
        ]


# https://wiki.videolan.org/Android_Player_Intents/
class AndroidVLCPlayer(Player):
    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None
    ) -> list[str]:
        args = [
            "am",
            "start",
            "--user",
            "0",
            "-a"
            "android.intent.action.VIEW",
            "-d",
            url,
            "-n",
            "org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity"
        ]
        if title:
            args.append("-e")
            args.append("title")
            args.append(title)
        return args
