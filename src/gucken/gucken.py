import logging
from atexit import register as register_atexit
from asyncio import gather
from os import name as os_name, remove
from .settings import gucken_settings_manager
from random import choice
from shutil import which
from subprocess import PIPE, Popen, DEVNULL
from time import sleep, time
from typing import Union, ClassVar, List

from pypresence import AioPresence, DiscordNotFound
from textual import events, on, work
from textual.app import App, ComposeResult
from textual.binding import BindingType, Binding
from textual.containers import Center, Container, Horizontal, ScrollableContainer
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    RadioButton,
    TabbedContent,
    TabPane,
)

from .utils import detect_player, is_android
from .custom_widgets import SortableTable
from .update import check
from .aniskip import (
    get_timings_from_search,
    timings_to_mpv_options,
    generate_chapters_file,
    get_chapters_file_mpv_option,
)
from .hoster.common import DirectLink, Hoster
from .hoster.doodstream import DoodstreamHoster
from .hoster.streamtape import StreamtapeHoster
from .hoster.veo import VOEHoster
from .hoster.vidoza import VidozaHoster
from .player.mpv import MPVPlayer
from .player.vlc import VLCPlayer
from .provider.aniworld import AniWorldProvider
from .provider.common import Episode, Language, SearchResult, Series
from .provider.serienstream import SerienStreamProvider
from platformdirs import user_log_path, user_config_path

logs_path = user_log_path("gucken", ensure_exists=True)
logging.basicConfig(
    filename=logs_path.joinpath("gucken.log"),
    encoding="utf-8",
    level=logging.INFO
)

register_atexit(gucken_settings_manager.save)


def sort_favorite_lang(language_list: List[Language], pio_list: List[str]) -> List[Language]:
    def lang_sort_key(hoster: Language) -> int:
        try:
            return pio_list.index(hoster.name)
        except ValueError:
            return len(pio_list)

    return sorted(language_list, key=lang_sort_key)


"""
def sort_favorite_hoster(hoster_list: List[Hoster], pio_list: List[Type[Hoster]]) -> List[Hoster]:
    def hoster_sort_key(hoster: Hoster) -> int:
        try:
            return pio_list.index(type(hoster))
        except ValueError:
            return len(pio_list)

    return sorted(hoster_list, key=hoster_sort_key)
"""


def sort_favorite_hoster(hoster_list: list[Hoster]) -> list[Hoster]:
    return sorted(
        hoster_list,
        key=lambda x: (
            not isinstance(x, StreamtapeHoster),
            not isinstance(x, VOEHoster),
            not isinstance(x, VidozaHoster),
            not isinstance(x, DoodstreamHoster),
        ),
    )


async def get_working_direct_link(hosters: list[Hoster]) -> Union[DirectLink, None]:
    for hoster in hosters:
        direct_link = await hoster.get_direct_link()
        is_working = await direct_link.check_is_working()
        logging.info(
            'Check: "%s" Working: "%s" URL: "%s"',
            type(hoster).__name__,
            is_working,
            direct_link,
        )
        if is_working:
            return direct_link
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


def move_item(lst: list, from_index: int, to_index: int) -> list:
    item = lst.pop(from_index)
    lst.insert(to_index, item)
    return lst


client_id = "1238219157464416266"


class GuckenApp(App):
    TITLE = "Gucken TUI"
    # TODO: color theme https://textual.textualize.io/guide/design/#designing-with-colors

    CSS_PATH = ["gucken.css"]
    custom_css = user_config_path("gucken").joinpath("custom.css")
    if custom_css.exists():
        CSS_PATH.append(custom_css)
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quit", show=True, priority=False),
    ]

    def __init__(self):
        super().__init__()
        self.current: Union[list[SearchResult], None] = None
        self.current_info: Union[Series, None] = None
        self.player = detect_player()
        self.RPC: Union[AioPresence, None] = None

        language: list = gucken_settings_manager.settings["settings"]["language"]
        language = remove_none_lang_keys(language)

        for ll in Language:
            language.append(ll.name)

        gucken_settings_manager.settings["settings"]["language"] = remove_duplicates(language)
        self.language = gucken_settings_manager.settings["settings"]["language"]

    def compose(self) -> ComposeResult:
        settings = gucken_settings_manager.settings["settings"]
        providers = settings["providers"]
        yield Header()
        with TabbedContent():
            with TabPane("Search", id="search"):  # Search "🔎"
                with Horizontal(id="hosters"):
                    yield Checkbox("AniWorld.to", value=providers["aniworld_to"], id="aniworld_to")
                    yield Checkbox("SerienStream.to", value=providers["serienstream_to"], id="serienstream_to")
                yield Input(id="input", placeholder="Search for a Anime")
                yield ListView(id="results")
            with TabPane("Info", id="info", disabled=True):  # Info "ℹ"
                with ScrollableContainer(id="res_con"):
                    yield Markdown(id="markdown")
                    yield ClickableDataTable(id="season_list")
            with TabPane("Settings", id="setting"):  # Settings "⚙"
                # TODO: dont show unneeded on android
                with Container():
                    yield SortableTable(id="lang")
                    yield RadioButton("Fullscreen", id="fullscreen", value=settings["fullscreen"])
                    yield RadioButton("Syncplay", id="syncplay", value=settings["syncplay"])
                    yield RadioButton("ani-skip", id="ani-skip", value=settings["ani-skip"])
                    yield RadioButton("Discord Presence", id="discord_presence", value=settings["discord_presence"])
            # with RadioSet():
            #    yield RadioButton("VOE", id="voe", value=True)
            #    yield RadioButton("Doodstream", id="doodstream")
            #    yield RadioButton("Vidoza", id="vidoza")
            #    yield RadioButton("Streamtape", id="streamtape")
        with Footer():
            with Center():
                yield Label("Made by Commandcracker with [red]:heart:[/red]")

    # TODO: dont lock - no async
    async def on_mount(self) -> None:
        lang = self.query_one("#lang", DataTable)
        lang.add_columns("Language")
        for l in self.language:
            lang.add_row(l)
        self.query_one(Input).focus()
        # TODO: FIx sometimes not disabling loading
        # TODO: dont lock
        self.query_one("#info", TabPane).loading = True
        table = self.query_one("#season_list", DataTable)
        table.cursor_type = "row"
        # TODO: make them scale
        table.add_columns("FT", "S", "F", "Title", "Hoster", "Sprache")
        if self.player is None:
            self.notify(
                "You wont be able to play videos.\n"
                "Without an supported video player!",
                title="No player found",
                severity="warning",
            )
        self.update_check()
        # TODO: dont lock
        if self.query_one("#discord_presence", RadioButton).value is True:
            await self.enable_RPC()
        else:
            await self.disable_RPC()

    async def enable_RPC(self):
        if self.RPC is None:
            self.RPC = AioPresence(client_id)
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

    async def on_checkbox_changed(self, event: Checkbox.Changed):
        gucken_settings_manager.settings["settings"]["providers"][event.control.id] = event.value
        self.lookup_anime(self.query_one("#input", Input).value)

    async def on_radio_button_changed(self, event: RadioButton.Changed):
        gucken_settings_manager.settings["settings"][event.control.id] = event.value
        if event.radio_button.id == "discord_presence":
            if event.value is True:
                await self.enable_RPC()
            else:
                await self.disable_RPC()

    async def on_sortable_table_sort_changed(self, event: SortableTable.SortChanged) -> None:
        move_item(self.language, event.previous, event.now)

    async def on_input_changed(self, message: Input.Changed) -> None:
        if message.value:
            self.lookup_anime(message.value)
        else:
            # TODO: fix sometimes wont clear
            await self.query_one("#results", ListView).clear()

    # TODO: https://textual.textualize.io/guide/workers/#thread-workers
    @work(exclusive=True)
    async def lookup_anime(self, keyword: str) -> None:
        search_providers = []
        if self.query_one("#aniworld_to", Checkbox).value:
            search_providers.append(AniWorldProvider.search(keyword))

        if self.query_one("#serienstream_to", Checkbox).value:
            search_providers.append(SerienStreamProvider.search(keyword))

        results_list_view = self.query_one("#results", ListView)
        await results_list_view.clear()
        results_list_view.loading = True
        results = await gather(*search_providers)
        final_results = []
        for l in results:
            if l is not None:
                for e in l:
                    final_results.append(e)

        # TODO: Sort final_results with fuzzy-sort
        if len(final_results) > 0:
            self.current = final_results
            for series in final_results:
                # TODO: show provider
                await results_list_view.append(ClickableListItem(Markdown(
                    f"##### {series.name} {series.production_year}\n{series.description}"
                )))
        results_list_view.loading = False
        if len(final_results) > 0:

            def select_first_index():
                try:
                    results_list_view.index = 0
                except AssertionError:
                    pass

            self.app.call_later(select_first_index)

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
        dt.loading = True
        index = self.app.query_one("#results", ListView).index
        series_search_result = self.current[index]
        self.play(series_search_result=series_search_result, episodes=self.current_info.episodes, index=dt.cursor_row)
        dt.loading = False

    @work(exclusive=True)
    async def open_info(self) -> None:
        series_search_result: SearchResult = self.current[self.app.query_one("#results", ListView).index]
        info_tab = self.query_one("#info", TabPane)
        info_tab.disabled = False
        info_tab.loading = True
        self.query_one(TabbedContent).active = "info"
        md = self.query_one("#markdown", Markdown)
        series = await series_search_result.get_series()
        self.current_info = series
        await md.update(series.to_markdown())

        table = self.query_one("#season_list", DataTable)
        table.clear()
        c = 0
        for ep in series.episodes:
            hl = []
            for h in ep.available_hoster:
                if h is VOEHoster:
                    hl.append("VEO")
                if h is DoodstreamHoster:
                    hl.append("D")
                if h is VidozaHoster:
                    hl.append("VZ")
                if h is StreamtapeHoster:
                    hl.append("ST")

            ll = []
            for l in ep.available_language:
                ll.append(l.name)

            c += 1
            table.add_row(
                c,
                ep.season,
                ep.episode_number,
                ep.title,
                " ".join(hl),
                " ".join(ll)
            )
        table.focus(scroll_visible=False)
        info_tab.loading = False

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
            self,
            series_search_result: SearchResult,
            episodes: list[Episode],
            index: int
    ) -> None:
        episode: Episode = episodes[index]
        processed_hoster = await episode.process_hoster()

        if len(episode.available_language) <= 0:
            self.notify(
                "The episode you are trying to watch has no stream available.",
                title="No stream available",
                severity="error",
            )
            return

        lang = sort_favorite_lang(episode.available_language, self.language)[0]
        sorted_hoster = sort_favorite_hoster(processed_hoster.get(lang))
        direct_link = await get_working_direct_link(sorted_hoster)

        # TODO: check for header support

        if self.player is None:
            self.notify(
                "You wont be able to play videos.\n"
                "Without an supported video player!",
                title="No player found",
                severity="error",
            )
            return

        # TODO: ani_skip, syncplay, fullscreen as cli arg
        # TODO: pass ani_skip as script
        ani_skip = self.query_one("#ani-skip", RadioButton).value
        syncplay = self.query_one("#syncplay", RadioButton).value
        fullscreen = self.query_one("#fullscreen", RadioButton).value

        title = f"{series_search_result.name} - {episode.title}"
        args = self.player.play(direct_link.url, title, fullscreen, direct_link.headers)

        if self.RPC and self.RPC.sock_writer:
            async def update():
                await self.RPC.update(
                    # state="00:20:00 / 00:25:00 57% complete",
                    details=title[:128],
                    large_text=title,
                    large_image=series_search_result.cover,
                    # small_image as playing or stopped ?
                    # small_image="https://jooinn.com/images/lonely-tree-reflection-3.jpg",
                    # small_text="ff 15",
                    # start=time.time(), # for paused
                    # end=time.time() + timedelta(minutes=20).seconds   # for time left
                )

            self.app.call_later(update)

        chapters_file = None

        # TODO: cache more
        if isinstance(self.player, MPVPlayer):
            if ani_skip is True:
                timings = await get_timings_from_search(series_search_result.name, index + 1)
                if timings:
                    chapters_file = generate_chapters_file(timings)

                    def delete_chapters_file():
                        try:
                            remove(chapters_file.name)
                        except FileNotFoundError:
                            pass

                    register_atexit(delete_chapters_file)
                    # --start=00:56
                    args += [
                        timings_to_mpv_options(timings),
                        get_chapters_file_mpv_option(chapters_file.name)
                    ]

        if syncplay:
            # TODO: make work with flatpak
            # TODO: make work with android
            syncplay_path = None
            if which("syncplay"):
                syncplay_path = "syncplay"
            if not syncplay_path:
                if os_name == "nt":
                    if which(r"C:\Program Files (x86)\Syncplay\Syncplay.exe"):
                        syncplay_path = r"C:\Program Files (x86)\Syncplay\Syncplay.exe"
            if not syncplay_path:
                self.notify(
                    "Syncplay not found",
                    title="Syncplay not found",
                    severity="error",
                )
            else:
                # TODO: add mpv.net, IINA, MPC-BE, MPC-HE, celluloid ?
                if isinstance(self.player, MPVPlayer) or isinstance(self.player, VLCPlayer):
                    player_path = which(args[0])
                    url = args[1]
                    args.pop(0)
                    args.pop(0)
                    args = [syncplay_path, "--player-path", player_path, url, "--"] + args
                else:
                    self.notify(
                        "Your player is not supported by Syncplay",
                        title="Player not supported",
                        severity="warning",
                    )

        logging.info("Running: %s", args)
        # TODO: detach on linux
        # multiprocessing
        # child_pid = os.fork()
        # if child_pid == 0:
        process = Popen(args, stderr=PIPE, stdout=DEVNULL, stdin=DEVNULL)
        while not self.app._exit:
            sleep(0.1)

            resume_time = None

            # only if mpv
            while not self.app._exit:
                output = process.stderr.readline()
                if process.poll() is not None:
                    break
                if output:
                    out_s = output.strip().decode()
                    # AV: 00:11:57 / 00:24:38 (49%) A-V:  0.000 Cache: 89s/22MB
                    if out_s.startswith("AV:"):
                        sp = out_s.split(" ")
                        resume_time = sp[1]

            if resume_time:
                logging.info("Resume: %s", resume_time)

            exit_code = process.poll()

            if exit_code is not None:
                if chapters_file:
                    try:
                        remove(chapters_file.name)
                    except FileNotFoundError:
                        pass
                if self.RPC and self.RPC.sock_writer:
                    self.app.call_later(self.RPC.clear)

                async def push_next_screen():
                    async def play_next(should_next):
                        if should_next:
                            self.play(
                                series_search_result,
                                episodes,
                                index + 1,
                            )

                    await self.app.push_screen(
                        Next("Playing next episode in", no_time=is_android), callback=play_next)

                if not len(episodes) <= index + 1:
                    self.app.call_later(push_next_screen)
                else:
                    # TODO: ask to mark as completed
                    pass
                return


exit_quotes = [
    "Closing one anime is just an invitation to open another.",
    "You finished one, now finish the next.",
    "Don't stop now, there's a whole universe waiting to be explored.",
    "The end of one journey is just the beginning of another.",
    "Like a phoenix rising from the ashes, the end of one episode ignites the flames of anticipation for the next."
]


def main():
    gucken_app = GuckenApp()
    gucken_app.run()
    print(choice(exit_quotes))


if __name__ == "__main__":
    main()
