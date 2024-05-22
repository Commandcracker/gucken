from pathlib import Path
from typing import Dict, Union

import toml
from platformdirs import user_config_path


def _merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge
    """
    merged = dict1.copy()
    for key, value in dict2.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = _merge_dicts(merged[key], value)
            else:
                merged[key] = value
        else:
            merged[key] = value
    return merged


def _load_settings(file_path: Union[str, Path], default_settings: Dict) -> Dict:
    try:
        with open(file_path, "r") as file:
            loaded_settings = toml.load(file)
    except FileNotFoundError:
        loaded_settings = {}
    return _merge_dicts(default_settings, loaded_settings)


def _save_settings(settings: Dict, file_path: Union[str, Path]) -> None:
    with open(file_path, "w") as file:
        toml.dump(settings, file)


class SettingsManager:
    def __init__(
        self,
        default_settings_file: Path,
        settings_file: Path,
        load_on_init=True,
        save_on_load=True,
    ):
        super().__init__()
        self.default_settings_file = default_settings_file
        self.settings_file = settings_file
        self.save_on_load = save_on_load
        self.settings: Union[Dict, None] = None
        if load_on_init:
            self.load()

    def load(self):
        with open(self.default_settings_file, "r") as file:
            default_settings = toml.load(file)

        self.settings = _load_settings(self.settings_file, default_settings)

        if self.save_on_load:
            self.save()

    def save(self):
        self.settings_file.parent.mkdir(exist_ok=True, parents=True)
        _save_settings(self.settings, self.settings_file)


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


class GuckenSettingsManager(Singleton, SettingsManager):
    pass


gucken_settings_manager = GuckenSettingsManager(
    default_settings_file=Path(__file__).parent.joinpath("resources", "default_settings.toml"),
    settings_file=user_config_path("gucken").joinpath("settings.toml"),
)
