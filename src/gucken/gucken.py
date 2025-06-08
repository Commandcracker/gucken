import argparse
import logging
from asyncio import gather, set_event_loop, new_event_loop
from atexit import register as register_atexit
from os import remove, name as os_name
from os.path import join
from pathlib import Path
from random import choice
from shutil import which
from subprocess import DEVNULL, PIPE, Popen
from time import sleep, time
from typing import ClassVar, List, Union
from async_lru import alru_cache
from os import getenv
from io import BytesIO

from fuzzywuzzy import fuzz
from platformdirs import user_config_path, user_log_path
from pypresence import AioPresence, DiscordNotFound
from rich.markup import escape
from textual import events, on, work
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Container, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    Collapsible,
    DataTable,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    RadioButton,
    Select,
    TabbedContent,
    TabPane,
)
from textual.worker import get_current_worker
from textual_image.widget import Image
from rich_argparse import RichHelpFormatter

from .db import (
    is_in_watchlist,
    remove_from_watchlist,
    add_to_watchlist,
    get_watchlist,
    remove_watchtime,
    mark_episode_watched,
    save_watchtime,
    init_db,
    get_unfinished_watchtime,
    is_episode_watched
)
from .aniskip import (
    generate_chapters_file,
    get_timings_from_search
)

from .custom_widgets import SortableTable
from .hoster._hosters import hoster
from .hoster.common import DirectLink, Hoster
from .player._players import all_players_keys, available_players_keys, player_map
from .player.mpv import MPVPlayer
from .player.vlc import VLCPlayer
from .provider.aniworld import AniWorldProvider
from .provider.common import Episode, Language, SearchResult, Series
from .provider.serienstream import SerienStreamProvider
from .settings import gucken_settings_manager
from .update import check
from .utils import detect_player, is_android, set_default_vlc_interface_cfg, get_vlc_intf_user_path
from .networking import AsyncClient
from . import __version__


def sort_favorite_lang(
        language_list: List[Language], pio_list: List[str]
) -> List[Language]:
    def lang_sort_key(hoster: Language) -> int:
        try:
            return pio_list.index(hoster.name)
        except ValueError:
            return len(pio_list)

    return sorted(language_list, key=lang_sort_key)


def sort_favorite_hoster(
        hoster_list: List[Hoster], pio_list: List[str]
) -> List[Hoster]:
    def hoster_sort_key(_hoster: Hoster) -> int:
        try:
            return pio_list.index(hoster.get_key(type(_hoster)))
        except ValueError:
            return len(pio_list)

    return sorted(hoster_list, key=hoster_sort_key)


def sort_favorite_hoster_by_key(
        hoster_list: List[str], pio_list: List[str]
) -> List[str]:
    def hoster_sort_key(_hoster: str) -> int:
        try:
            return pio_list.index(_hoster)
        except ValueError:
            return len(pio_list)

    return sorted(hoster_list, key=hoster_sort_key)


async def get_working_direct_link(hosters: list[Hoster], app: "GuckenApp") -> Union[DirectLink, None]:
    for hoster in hosters:
        name = type(hoster).__name__
        try:
            direct_link = await hoster.get_direct_link()
        except Exception:
            logging.warning(
                "%s: failed to retrieve video URL from: \"%s\"",
                name,
                hoster.url,
                exc_info=True
            )
            app.notify(
                "Failed to retrieve video URL",
                title=f"{name} error",
                severity="warning",
            )
            continue
        if not direct_link or not direct_link.url or not isinstance(direct_link.url, str) or not isinstance(direct_link, DirectLink):
            logging.warning(
                "%s: Returned empty URL: \"%s\"",
                name,
                hoster.url
            )
            app.notify(
                "Returned empty URL",
                title=f"{name} error",
                severity="warning",
            )
            continue
        is_working = await direct_link.check_is_working()
        if is_working:
            return direct_link
        else:
            logging.warning(
                "%s: Video URL is not working: \"%s\"",
                name,
                direct_link.url or "None"
            )
            app.notify(
                "Video URL is not working",
                title=f"{name} error",
                severity="warning",
            )
    return None


class Next(ModalScreen):
    time = reactive(3)

    def __init__(self, question: str, no_time: bool = False):
        super().__init__()
        self.question = question
        self.no_time = no_time

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(self.question)
            with Horizontal():
                yield Button.error("Cancel", id="cancel")
                yield Button.success("Next", id="next")

    def on_mount(self) -> None:
        if not self.no_time:
            self.set_interval(1, self.update_time)
            self.query_one(Label).update(self.question + " " + str(self.time))

    def update_time(self) -> None:
        self.time = self.time - 1
        if self.time < 0:
            self.dismiss(True)
        self.query_one(Label).update(self.question + " " + str(self.time))

    @on(Button.Pressed)
    def exit_screen(self, event):
        button_id = event.button.id
        self.dismiss(button_id == "next")


class ClickableListItem(ListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_click = None

    def on_click(self) -> None:
        if self.last_click and time() - self.last_click < 0.5:
            self.app.open_info()
        self.last_click = time()


class ClickableDataTable(DataTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_click = {}

    def on_click(self, event: events.Click) -> None:
        meta = event.style.meta
        if not "row" in meta or not "column" in meta:
            return
        row_index = meta["row"]
        if row_index <= -1:
            return
        if self.last_click.get(row_index) and time() - self.last_click[row_index] < 0.5:
            self.app.play_selected()
        self.last_click[row_index] = time()


def remove_duplicates(lst: list) -> list:
    """
    Why this instead of a set you ask ?
    Because a set cant maintaining the original order.
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def remove_none_lang_keys(lst: list) -> list:
    valid_languages = {lang.name for lang in Language}
    return [item for item in lst if item in valid_languages]


def remove_none_host_keys(lst: list) -> list:
    valid_host = {h for h in hoster}
    return [item for item in lst if item in valid_host]


def move_item(lst: list, from_index: int, to_index: int) -> list:
    item = lst.pop(from_index)
    lst.insert(to_index, item)
    return lst


CLIENT_ID = "1238219157464416266"

class ContinueWatchScreen(ModalScreen):
    def __init__(self, question, callback):
        super().__init__()
        self.question = question
        self.callback = callback

    def compose(self):
        with Container():
            yield Label(self.question)
            with Horizontal():
                yield Button("Nein", id="no")
                yield Button("Ja", id="yes")

    @on(Button.Pressed)
    def handle_button(self, event):
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def on_dismiss(self, result):
        self.callback(result)

class GuckenApp(App):
    TITLE = f"Gucken {__version__}"
    CSS_PATH = [join("resources", "gucken.css")]
    custom_css = user_config_path("gucken").joinpath("custom.css")
    if custom_css.exists():
        CSS_PATH.append(custom_css)
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit", show=False, priority=False),
    ]

    init_db()

    # TODO: theme_changed_signal

    def __init__(self, debug: bool, search: str):
        super().__init__(watch_css=debug)
        self._debug = debug
        self._search = search

        self.current: Union[list[SearchResult], None] = None
        self.current_info: Union[Series, None] = None
        self.detected_player = detect_player()
        self.RPC: Union[AioPresence, None] = None
        self.unfinished = get_unfinished_watchtime()

        if self.unfinished:
            self.ask_next_unfinished()

        language: list = gucken_settings_manager.settings["settings"]["language"]
        language = remove_none_lang_keys(language)

        for ll in Language:
            language.append(ll.name)

        gucken_settings_manager.settings["settings"]["language"] = remove_duplicates(
            language
        )
        self.language = gucken_settings_manager.settings["settings"]["language"]

        _hoster: list = gucken_settings_manager.settings["settings"]["hoster"]
        _hoster = remove_none_host_keys(_hoster)

        for ll in hoster:
            _hoster.append(ll)

        gucken_settings_manager.settings["settings"]["hoster"] = remove_duplicates(
            _hoster
        )
        self.hoster = gucken_settings_manager.settings["settings"]["hoster"]

    def ask_next_unfinished(self, i=0):
        if i >= len(self.unfinished):
            return
        series, season, episode, provider, time_str = self.unfinished[i]
        question = f"Du hast '{series}' S{season}E{episode} [{provider}] noch nicht zu Ende geschaut. Weiterschauen ab {time_str}?"

        def on_answer(result):
            if result:
                # Hier Wiedergabe starten, z.B.:
                # self.play_from_watchtime(series, season, episode, provider, time_str)
                pass
            else:
                self.ask_next_unfinished(i + 1)

        self.push_screen(ContinueWatchScreen(question, on_answer))

    def compose(self) -> ComposeResult:
        settings = gucken_settings_manager.settings["settings"]
        providers = settings["providers"]

        player = settings["player"]["player"]
        if player not in all_players_keys:
            player = "AutomaticPlayer"

        yield Header()
        with TabbedContent():
            with TabPane("Search", id="search"):  # Search "🔎"
                with Horizontal(id="hosters"):
                    yield Checkbox(
                        "AniWorld.to",
                        value=providers["aniworld_to"],
                        id="aniworld_to",
                        classes="provider"
                    )
                    yield Checkbox(
                        "SerienStream.to",
                        value=providers["serienstream_to"],
                        id="serienstream_to",
                        classes="provider"
                    )
                yield Input(id="input", placeholder="Search for a Anime")
                yield ListView(id="results")

            with TabPane("Info", id="info", disabled=True):  # Info "ℹ"
                with ScrollableContainer(id="res_con"):
                    yield Horizontal(
                        Image(id="image"),
                        Markdown(id="markdown"),
                        id="res_con_2"
                    )
                    yield Button(
                        "Zur Watchlist hinzufügen",
                        id="watchlist_btn",
                        variant="success"
                    )
                    yield Select.from_values(
                        [],  # Leere Liste zu Beginn
                        id="season_filter",
                        prompt="Alle Staffeln"
                    )
                    yield ClickableDataTable(id="season_list")
            with TabPane("Watchlist", id="watchlist"):
                yield ListView(id="watchlist_view")
            with TabPane("Settings", id="setting"):  # Settings "⚙"
                # TODO: dont show unneeded on android
                with ScrollableContainer(id="settings_container"):
                    yield SortableTable(id="lang")
                    yield SortableTable(id="host")
                    yield RadioButton(
                        "Image display",
                        id="image_display",
                        value=settings["image_display"],
                    )
                    yield RadioButton(
                        "Update checker",
                        id="update_checker",
                        value=settings["update_checker"],
                    )
                    yield RadioButton(
                        "Discord Presence",
                        id="discord_presence",
                        value=settings["discord_presence"],
                    )
                    with Collapsible(title="Player", collapsed=False):
                        yield RadioButton(
                            "Fullscreen", id="fullscreen", value=settings["fullscreen"]
                        )
                        yield RadioButton(
                            "Syncplay", id="syncplay", value=settings["syncplay"]
                        )
                        yield RadioButton(
                            "Autoplay",
                            id="autoplay",
                            value=settings["autoplay"]["enabled"],
                        )
                        yield RadioButton(
                            "PiP Mode (MPV & VLC only)",
                            id="pip",
                            value=settings["pip"],
                        )
                        yield Select.from_values(
                            available_players_keys,
                            id="player",
                            prompt="AutomaticPlayer",
                            value=(
                                Select.BLANK if player == "AutomaticPlayer" else player
                            ),
                        )
                    with Collapsible(title="ani-skip (MPV & VLC only)", collapsed=False):
                        yield RadioButton(
                            "Skip opening",
                            id="ani_skip_opening",
                            value=settings["ani_skip"]["skip_opening"],
                        )
                        yield RadioButton(
                            "Skip ending",
                            id="ani_skip_ending",
                            value=settings["ani_skip"]["skip_ending"],
                        )
                        yield RadioButton(
                            "Get chapters (only MPV)",
                            id="ani_skip_chapters",
                            value=settings["ani_skip"]["chapters"],
                        )
        # yield Footer()
        with Center(id="footer"):
            yield Label("Made by Commandcracker with [red]❤[/red]")

    @on(Input.Changed)
    async def input_changed(self, event: Input.Changed):
        if event.control.id == "input":
            self.lookup_anime(event.value)

    @on(Select.Changed)
    def on_season_filter_changed(self, event: Select.Changed) -> None:
        if event.control.id == "season_filter":
            table = self.query_one("#season_list", DataTable)
            if not self.current_info:
                return

            table.clear(columns=True)
            table.add_columns("FT", "S", "F", "Title", "Hoster", "Sprache")

            # Liste der gefilterten Episoden speichern
            self.filtered_episodes = []

            # Temporäre Listen für die Sortierung
            regular_episodes = []
            movie_episodes = []

            # Episoden in reguläre und Filme aufteilen
            for ep in self.current_info.episodes:
                if event.value == Select.BLANK or str(ep.season) == event.value:
                    if str(ep.season) == "0":
                        movie_episodes.append(ep)
                    else:
                        regular_episodes.append(ep)

            # Zusammenführen der Listen: erst reguläre Episoden, dann Filme
            sorted_episodes = regular_episodes + movie_episodes
            self.filtered_episodes = sorted_episodes

            # Anzeigen der sortierten Episoden
            c = 0
            for ep in sorted_episodes:
                hl = []
                for h in ep.available_hoster:
                    hl.append(hoster.get_key(h))

                ll = []
                for l in sort_favorite_lang(ep.available_language, self.language):
                    ll.append(l.name)

                c += 1
                table.add_row(
                    c,
                    "F" if str(ep.season) == "0" else ep.season,
                    ep.episode_number,
                    escape(ep.title),
                    " ".join(sort_favorite_hoster_by_key(hl, self.hoster)),
                    " ".join(ll),
                )

    @on(SortableTable.SortChanged)
    async def sortableTable_sortChanged(
            self,
            event: SortableTable.SortChanged
    ):
        id = event.control.id
        if id == "lang":
            move_item(self.language, event.previous, event.now)
            return

        if id == "host":
            move_item(self.hoster, event.previous, event.now)
            return

    @on(Checkbox.Changed)
    async def checkbox_changed(self, event: Checkbox.Changed):
        id = event.control.id
        settings = gucken_settings_manager.settings["settings"]

        if event.control.has_class("provider"):
            settings["providers"][id] = event.value
            self.lookup_anime(self.query_one("#input", Input).value)

    @on(RadioButton.Changed)
    async def radio_button_changed(self, event: RadioButton.Changed):
        id = event.control.id
        settings = gucken_settings_manager.settings["settings"]

        if id == "ani_skip_opening":
            settings["ani_skip"]["skip_opening"] = event.value
            return

        if id == "ani_skip_ending":
            settings["ani_skip"]["skip_ending"] = event.value
            return

        if id == "ani_skip_chapters":
            settings["ani_skip"]["chapters"] = event.value
            return

        if id == "autoplay":
            settings["autoplay"]["enabled"] = event.value
            return

        if id == "pip":
            settings["pip"] = event.value
            return

        if id == "image_display" and event.value == False:
            img: Image = self.query_one("#image", Image)
            img.image = None

        settings[id] = event.value

        if id == "discord_presence":
            if event.value is True:
                await self.enable_RPC()
            else:
                await self.disable_RPC()

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        id = event.control.id
        settings = gucken_settings_manager.settings["settings"]

        if id == "player":
            if event.value == Select.BLANK:
                settings["player"]["player"] = "AutomaticPlayer"
            else:
                settings["player"]["player"] = event.value

    # TODO: dont lock - no async
    async def on_mount(self) -> None:
        self.theme = getenv("TEXTUAL_THEME") or gucken_settings_manager.settings["settings"]["ui"]["theme"]

        self.update_watchlist_view()

        def on_theme_change(old_value: str, new_value: str) -> None:
            gucken_settings_manager.settings["settings"]["ui"]["theme"] = new_value

        self.watch(self.app, "theme", on_theme_change, init=False)

        lang = self.query_one("#lang", DataTable)
        lang.add_columns("Language")
        for l in self.language:
            lang.add_row(l)

        host = self.query_one("#host", DataTable)
        host.add_columns("Host")
        for h in self.hoster:
            host.add_row(h)

        _input = self.query_one("#input", Input)
        _input.focus()

        if self._search is not None:
            def set_search():
                _input.value = self._search

            self.call_later(set_search)

        self.query_one("#info", TabPane).set_loading(True)

        table = self.query_one("#season_list", DataTable)
        table.cursor_type = "row"

        if self.query_one("#update_checker", RadioButton).value is True:
            self.update_check()

        # TODO: dont lock
        if self.query_one("#discord_presence", RadioButton).value is True:
            await self.enable_RPC()
        else:
            await self.disable_RPC()

    async def enable_RPC(self):
        if self.RPC is None:
            self.RPC = AioPresence(CLIENT_ID)
        try:
            await self.RPC.connect()
        except DiscordNotFound:
            pass

    async def disable_RPC(self):
        if self.RPC is not None:
            await self.RPC.clear()
            # close without closing event loop
            self.RPC.send_data(2, {"v": 1, "client_id": self.RPC.client_id})
            self.RPC.sock_writer.close()
            self.RPC = None

    @alru_cache(maxsize=64, ttl=600)  # Cache 64 entries. Clear entry after 10 minutes.
    async def aniworld_search(self, keyword: str) -> Union[list[SearchResult], None]:
        return await AniWorldProvider.search(keyword)

    @alru_cache(maxsize=64, ttl=600)  # Cache 64 entries. Clear entry after 10 minutes.
    async def serienstream_search(self, keyword: str) -> Union[list[SearchResult], None]:
        return await SerienStreamProvider.search(keyword)

    def sync_gather(self, tasks: list):
        async def gather_all():
            return await gather(*tasks)

        loop = new_event_loop()
        set_event_loop(loop)
        return loop.run_until_complete(gather_all())

    # TODO: Exit on error when debug = true
    # TODO: sometimes not removing loading state
    # TODO: FIX
    """
    sys:1: RuntimeWarning: coroutine '_LRUCacheWrapperInstanceMethod.__call__' was never awaited
    RuntimeWarning: Enable tracemalloc to get the object allocation traceback
    """

    @work(exclusive=True, thread=True, exit_on_error=False)
    def lookup_anime(self, keyword: str) -> None:
        results_list_view = self.query_one("#results", ListView)
        worker = get_current_worker()

        if keyword is None:
            if not worker.is_cancelled:
                self.call_from_thread(results_list_view.clear)
                self.call_from_thread(results_list_view.set_loading, False)
            return

        aniworld_to = self.query_one("#aniworld_to", Checkbox).value
        serienstream_to = self.query_one("#serienstream_to", Checkbox).value

        search_providers = []

        if aniworld_to:
            search_providers.append(self.aniworld_search(keyword))
        if serienstream_to:
            search_providers.append(self.serienstream_search(keyword))

        if worker.is_cancelled:
            return
        self.call_from_thread(results_list_view.clear)
        self.call_from_thread(results_list_view.set_loading, True)
        if worker.is_cancelled:
            return
        results = self.sync_gather(search_providers)
        final_results = []
        for l in results:
            if l is not None:
                for e in l:
                    final_results.append(e)

        def fuzzy_sort_key(result):
            return fuzz.ratio(keyword, result.name)

        final_results = sorted(final_results, key=fuzzy_sort_key, reverse=True)
        if len(final_results) > 0:
            self.current = final_results
            items = []
            for series in final_results:
                items.append(ClickableListItem(
                    Markdown(
                        f"##### {series.name} {series.production_year} [{series.provider_name}]"
                        f"\n{series.description}"
                    )
                ))
            if worker.is_cancelled:
                return
            self.call_from_thread(results_list_view.extend, items)
        self.call_from_thread(results_list_view.set_loading, False)
        if len(final_results) > 0:

            def select_first_index():
                try:
                    results_list_view.index = 0
                except AssertionError:
                    pass

            self.call_later(select_first_index)

    async def on_key(self, event: events.Key) -> None:
        key = event.key
        if self.screen.id == "_default":
            if self.query_one(TabbedContent).active == "search":
                lv = self.query_one("#results", ListView)
                inp = self.query_one("#input", Input)
                # Down to list
                if key == "down":
                    if inp.has_focus:
                        lv.focus()
                # Up to Input
                if key == "up":
                    if not inp.has_focus and (lv.index == 0 or lv.index is None):
                        inp.focus()
                # Selection
                if key == "enter":
                    if lv.index is not None:
                        self.open_info()
                # Type anywhere
                if key not in ["down", "up", "enter"]:
                    if lv.has_focus:
                        inp.focus()
                        if key == "backspace":
                            inp.action_delete_left()
                        else:
                            await inp.on_event(event)
            if key == "enter" and self.query_one("#season_list", DataTable).has_focus:
                self.play_selected()

    @work(exclusive=True)
    async def play_selected(self):
        dt = self.query_one("#season_list", DataTable)
        # TODO: show loading
        # dt.set_loading(True)
        index = self.app.query_one("#results", ListView).index
        series_search_result = self.current[index]

        # Verwende filtered_episodes falls vorhanden, sonst current_info.episodes
        if hasattr(self, 'filtered_episodes') and self.filtered_episodes:
            episodes_to_use = self.filtered_episodes
            # cursor_row entspricht direkt dem Index in der gefilterten Liste
            selected_index = dt.cursor_row
        else:
            episodes_to_use = self.current_info.episodes
            # Finde die entsprechende Episode basierend auf der Tabellenzeile
            selected_row = dt.get_row_at(dt.cursor_row)
            # Suche die passende Episode anhand der angezeigten Informationen
            selected_index = next((i for i, ep in enumerate(episodes_to_use)
                                   if
                                   (str(ep.season) if ep.season != 0 else "F") == str(selected_row[1])  # Prüfe Staffel
                                   and str(ep.episode_number) == str(selected_row[2])), 0)  # Prüfe Episodennummer

        self.play(
            series_search_result=series_search_result,
            episodes=episodes_to_use,
            index=selected_index,
        )
        #dt.set_loading(False)

    @alru_cache(maxsize=32, ttl=600)  # Cache 32 entries. Clear entry after 10 minutes.
    async def get_series(self, series_search_result: SearchResult):
        return await series_search_result.get_series()

    @work(exclusive=True)
    async def open_info(self, name=None, provider=None) -> None:
        watchlist_btn = self.query_one("#watchlist_btn", Button)

        # Falls name und provider übergeben werden, suche das passende SearchResult
        if name and provider:
            # Suche in self.current
            series_search_result = None
            if self.current:
                for s in self.current:
                    if s.name == name and s.provider_name == provider:
                        series_search_result = s
                        break
            # Falls nicht gefunden, suche per Provider
            if not series_search_result:
                results = await gather(self.aniworld_search(name), self.serienstream_search(name))
                for result_list in results:
                    if result_list:
                        for s in result_list:
                            if s.name == name and s.provider_name == provider:
                                series_search_result = s
                                break
                    if series_search_result:
                        break
            if not series_search_result:
                return
            # Setze self.current auf das gefundene Ergebnis, damit alles wie gewohnt funktioniert
            self.current = [series_search_result]
            index = 0
        else:
            index = self.app.query_one("#results", ListView).index
            if index is None or not self.current or index >= len(self.current):
                return
            series_search_result: SearchResult = self.current[
                self.app.query_one("#results", ListView).index
            ]

        # Rest wie gehabt ...
        if is_in_watchlist(series_search_result):
            watchlist_btn.label = "Aus Watchlist entfernen"
            watchlist_btn.variant = "error"
        else:
            watchlist_btn.label = "Zur Watchlist hinzufügen"
            watchlist_btn.variant = "success"

        info_tab = self.query_one("#info", TabPane)
        info_tab.disabled = False
        info_tab.set_loading(True)
        table = self.query_one("#season_list", DataTable)
        table.focus(scroll_visible=False)
        md = self.query_one("#markdown", Markdown)

        series = await self.get_series(series_search_result)
        self.current_info = series

        season_filter = self.query_one("#season_filter", Select)
        unique_seasons = sorted(set(ep.season for ep in series.episodes))

        regular_seasons = [s for s in unique_seasons if s != 0]
        movies_season = [s for s in unique_seasons if s == 0]
        sorted_seasons = regular_seasons + movies_season

        season_filter_options = []
        for season in sorted_seasons:
            label = "Filme" if season == 0 else f"Staffel {season}"
            season_filter_options.append((label, str(season)))
        season_filter.set_options(season_filter_options)
        season_filter.value = Select.BLANK

        await md.update(series.to_markdown())

        if gucken_settings_manager.settings["settings"]["image_display"]:
            img: Image = self.query_one("#image", Image)
            async with AsyncClient(verify=False) as client:
                response = await client.get(series.cover)
                img.image = BytesIO(response.content)

        table.clear(columns=True)
        table.add_columns("FT", "S", "F", "Title", "Hoster", "Sprache")

        sorted_episodes = []
        for ep in series.episodes:
            if ep.season == "S":
                sorted_episodes.append(ep)
        for ep in series.episodes:
            if isinstance(ep.season, (int, str)) and ep.season not in ["S", 0]:
                sorted_episodes.append(ep)
        for ep in series.episodes:
            if ep.season == 0:
                sorted_episodes.append(ep)

        c = 0
        for ep in sorted_episodes:
            hl = [hoster.get_key(h) for h in ep.available_hoster]
            ll = [l.name for l in sort_favorite_lang(ep.available_language, self.language)]
            c += 1
            if ep.season == "S":
                season_display = "S"
            elif ep.season == 0:
                season_display = "F"
            else:
                season_display = ep.season

            watched = is_episode_watched(
                series_search_result.name,
                ep.season,
                ep.episode_number,
                series_search_result.provider_name
            )

            table.add_row(
                c,
                season_display,
                ep.episode_number,
                escape(ep.title),
                " ".join(sort_favorite_hoster_by_key(hl, self.hoster)),
                " ".join(ll),
            )
            info_tab.set_loading(False)

    @on(Button.Pressed)
    def on_watchlist_btn(self, event):
        if event.button.id == "watchlist_btn":
            index = self.app.query_one("#results", ListView).index
            if index is None:
                # Fallback: erstes Element aus self.current verwenden
                if not self.current:
                    return
                series = self.current[0]
            else:
                series = self.current[index]
            if is_in_watchlist(series):
                remove_from_watchlist(series)
                event.button.label = "Zur Watchlist hinzufügen"
                event.button.variant = "success"
            else:
                add_to_watchlist(series)
                event.button.label = "Aus Watchlist entfernen"
                event.button.variant = "error"
            self.update_watchlist_view()

    def update_watchlist_view(self):
        watchlist_view = self.query_one("#watchlist_view", ListView)
        watchlist_view.clear()
        for name, provider_name in get_watchlist():
            item = ClickableListItem(Markdown(f"##### {name} [{provider_name}]"))
            item.anime_name = name
            item.anime_provider_name = provider_name
            watchlist_view.append(item)

    @on(ListView.Selected, "#watchlist_view")
    async def on_watchlist_selected(self, event):
        item = event.item
        name = getattr(item, "anime_name", None)
        provider_name = getattr(item, "anime_provider_name", None)
        if name and provider_name:
            results = await gather(self.aniworld_search(name), self.serienstream_search(name))
            for result_list in results:
                if result_list:
                    for series in result_list:
                        if series.name == name and series.provider_name == provider_name:
                            self.current = [series]
                            self.call_later(lambda: self.open_info(name, provider_name))
                            return

    @work(exclusive=True, thread=True)
    async def update_check(self):
        res = await check()
        if res:
            self.notify(
                f"{res.current} -> {res.latest}\npip install -U gucken",
                title="Update available",
                severity="information",
            )

    @work(thread=True)
    async def play(
            self, series_search_result: SearchResult, episodes: list[Episode], index: int
    ) -> None:
        p = gucken_settings_manager.settings["settings"]["player"]["player"]
        if p == "AutomaticPlayer":
            _player = self.detected_player
        else:
            _player = player_map[p]()

        if _player is None:
            self.notify(
                "Please install a supported player!",
                title="No player detected",
                severity="error",
            )
            return

        if p != "AutomaticPlayer" and not _player.is_available():
            self.notify(
                "Your configured player has not been found!",
                title="Player not found",
                severity="error",
            )
            return

        episode: Episode = episodes[index]
        processed_hoster = await episode.process_hoster()

        if not episode.available_language:
            self.notify(
                "The episode you are trying to watch has no stream available.",
                title="No stream available",
                severity="error",
            )
            return

        lang = sort_favorite_lang(episode.available_language, self.language)[0]
        sorted_hoster = sort_favorite_hoster(processed_hoster.get(lang), self.hoster)
        direct_link = await get_working_direct_link(sorted_hoster, self)
        if not direct_link:
            self.notify(
                "No working stream found.",
                title="No stream available",
                severity="error",
            )
            return

        syncplay = gucken_settings_manager.settings["settings"]["syncplay"]
        fullscreen = gucken_settings_manager.settings["settings"]["fullscreen"]

        title = f"{series_search_result.name} S{episode.season}E{episode.episode_number} - {episode.title}"
        args = _player.play(direct_link.url, title, fullscreen, direct_link.headers)

        if self.RPC and self.RPC.sock_writer:
            async def update():
                await self.RPC.update(
                    details=title[:128],
                    large_text=title,
                    large_image=series_search_result.cover,
                )

            self.app.call_later(update)

        if gucken_settings_manager.settings["settings"]["pip"]:
            if isinstance(_player, MPVPlayer):
                args += ["--ontop", "--no-border", "--snap-window"]
            if isinstance(_player, VLCPlayer):
                args += ["--video-on-top", "--qt-minimal-view", "--no-video-deco"]

        if direct_link.force_hls and isinstance(_player, MPVPlayer):
            args += ["--demuxer=lavf", "--demuxer-lavf-format=hls"]

        if self._debug:
            logs_path = user_log_path("gucken", ensure_exists=True)
            if isinstance(_player, MPVPlayer):
                args.append("--log-file=" + str(logs_path.joinpath("mpv.log")))
            elif isinstance(_player, VLCPlayer):
                args += ["--file-logging", "--log-verbose=3", "--logfile=" + str(logs_path.joinpath("vlc.log"))]

        chapters_file = None

        if isinstance(_player, MPVPlayer) or isinstance(_player, VLCPlayer):
            ani_skip_opening = gucken_settings_manager.settings["settings"]["ani_skip"]["skip_opening"]
            ani_skip_ending = gucken_settings_manager.settings["settings"]["ani_skip"]["skip_ending"]
            ani_skip_chapters = gucken_settings_manager.settings["settings"]["ani_skip"]["chapters"]

            if ani_skip_opening or ani_skip_ending or ani_skip_chapters:
                timings = await get_timings_from_search(
                    series_search_result.name + " " + str(episode.season), episode.episode_number
                )
                if timings:
                    if isinstance(_player, MPVPlayer):
                        if ani_skip_chapters:
                            chapters_file = generate_chapters_file(timings)

                            def delete_chapters_file():
                                try:
                                    remove(chapters_file.name)
                                except FileNotFoundError:
                                    pass

                            register_atexit(delete_chapters_file)
                            args.append(f"--chapters-file={chapters_file.name}")
                        script_opts = []
                        if ani_skip_opening:
                            script_opts += [f"skip-op_start={timings.op_start}", f"skip-op_end={timings.op_end}"]
                        if ani_skip_ending:
                            script_opts += [f"skip-ed_start={timings.ed_start}", f"skip-ed_end={timings.ed_end}"]
                        if script_opts:
                            args.append(f"--script-opts={','.join(script_opts)}")
                        args.append(
                            "--scripts-append=" + str(Path(__file__).parent.joinpath("resources", "mpv_gucken.lua")))
                    if isinstance(_player, VLCPlayer):
                        prepend_data = []
                        if ani_skip_opening:
                            prepend_data += [set_default_vlc_interface_cfg("op_start", timings.op_start),
                                             set_default_vlc_interface_cfg("op_end", timings.op_end)]
                        if ani_skip_ending:
                            prepend_data += [set_default_vlc_interface_cfg("ed_start", timings.ed_start),
                                             set_default_vlc_interface_cfg("ed_end", timings.ed_end)]
                        vlc_intf_user_path = get_vlc_intf_user_path(_player.executable).vlc_intf_user_path
                        Path(vlc_intf_user_path).mkdir(mode=0o755, parents=True, exist_ok=True)
                        vlc_skip_plugin = Path(__file__).parent.joinpath("resources", "vlc_gucken.lua")
                        copy_to = join(vlc_intf_user_path, "vlc_gucken.lua")
                        with open(vlc_skip_plugin, 'r') as f:
                            original_content = f.read()
                        with open(copy_to, 'w') as f:
                            f.write("\n".join(prepend_data) + original_content)
                        args.append("--control=luaintf{intf=vlc_gucken}")

        if syncplay:
            syncplay_path = None
            if which("syncplay"):
                syncplay_path = "syncplay"
            if not syncplay_path and os_name == "nt":
                if which(r"C:\Program Files (x86)\Syncplay\Syncplay.exe"):
                    syncplay_path = r"C:\Program Files (x86)\Syncplay\Syncplay.exe"
            if not syncplay_path:
                self.notify(
                    "Syncplay not found",
                    title="Syncplay not found",
                    severity="error",
                )
            else:
                if isinstance(_player, MPVPlayer) or isinstance(_player, VLCPlayer):
                    player_path = which(args[0])
                    url = args[1]
                    args = [syncplay_path, "--player-path", player_path, url, "--"] + args[2:]
                else:
                    self.notify(
                        "Your player is not supported by Syncplay",
                        title="Player not supported",
                        severity="warning",
                    )

        logging.info("Running: %s", args)
        process = Popen(args, stderr=PIPE, stdout=DEVNULL, stdin=DEVNULL)
        while not self.app._exit:
            sleep(0.1)

            resume_time = None
        resume_time = None

        try:
            while not self.app._exit:
                sleep(0.1)
                if process.poll() is not None:
                    break
                output = process.stderr.readline()
                if output:
                    out_s = output.strip().decode(errors="ignore")
                    if out_s.startswith("AV:"):
                        sp = out_s.split(" ")
                        if len(sp) > 1:
                            resume_time = sp[1]  # Format: HH:MM:SS

            if resume_time is None or resume_time in ("00:00:00", "0:00:00"):
                remove_watchtime(
                    series_search_result.name,
                    episode.season,
                    episode.episode_number,
                    series_search_result.provider_name
                )
                mark_episode_watched(
                    series_search_result.name,
                    episode.season,
                    episode.episode_number,
                    series_search_result.provider_name
                )
                logging.info("Episode als gesehen markiert und Watchtime entfernt.")
            else:
                save_watchtime(
                    series_search_result.name,
                    episode.season,
                    episode.episode_number,
                    series_search_result.provider_name,
                    resume_time
                )
                logging.info("Resume-Time gespeichert: %s", resume_time)
        finally:
            if chapters_file:
                try:
                    remove(chapters_file.name)
                except FileNotFoundError:
                    pass
            if self.RPC and self.RPC.sock_writer:
                self.app.call_later(self.RPC.clear)

        exit_code = process.poll()
        if exit_code is not None:
            async def push_next_screen():
                async def play_next(should_next):
                    if should_next:
                        self.play(
                            series_search_result,
                            episodes,
                            index + 1,
                        )

                await self.app.push_screen(
                    Next("Playing next episode in", no_time=is_android),
                    callback=play_next,
                )

            autoplay = gucken_settings_manager.settings["settings"]["autoplay"]["enabled"]
            if len(episodes) > index + 1 and autoplay is True:
                self.app.call_later(push_next_screen)


exit_quotes = [
    "Closing one anime is just an invitation to open another.",
    "You finished one, now finish the next.",
    "Don't stop now, there's a whole universe waiting to be explored.",
    "The end of one journey is just the beginning of another.",
    "Like a phoenix rising from the ashes, the end of one episode ignites the flames of anticipation for the next.",
]


def main():
    parser = argparse.ArgumentParser(
        prog='gucken',
        description="Gucken is a Terminal User Interface which allows you to browse and watch your favorite anime's with style.",
        formatter_class=RichHelpFormatter
    )
    parser.add_argument("search", nargs='?')
    parser.add_argument(
        "--debug", "--dev",
        action="store_true",
        help='enables logging and live tcss reload'
    )
    parser.add_argument(
        '-V', '--version',
        action='store_true',
        help='display version information.'
    )
    args = parser.parse_args()
    if args.version:
        exit(f"gucken {__version__}")
    if args.debug:
        logs_path = user_log_path("gucken", ensure_exists=True)
        logging.basicConfig(
            filename=logs_path.joinpath("gucken.log"), encoding="utf-8", level=logging.INFO, force=True
        )

    register_atexit(gucken_settings_manager.save)
    print(f"\033]0;Gucken {__version__}\007", end='', flush=True)
    gucken_app = GuckenApp(debug=args.debug, search=args.search)
    gucken_app.run()
    print(choice(exit_quotes))


if __name__ == "__main__":
    main()