from .common import Player


def dict_to_string(dictionary):
    return ','.join([f"{key}: {value}" for key, value in dictionary.items()])


class MPVPlayer(Player):
    supports_headers = True

    def play(
            self,
            url: str,
            title: str,
            full_screen: bool,
            headers: dict[str, str] = None,
            override_executable: str = None,
            additional_arguments: list[str] = None
    ) -> list[str]:
        args = [
            override_executable or "mpv",
            url,
            "--fullscreen" if full_screen else "",
            f"--force-media-title={title}",
            f"--http-header-fields={dict_to_string(headers)}" if headers else "",
        ]
        if additional_arguments is not None:
            args += additional_arguments
        return args
