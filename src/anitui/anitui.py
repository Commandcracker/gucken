# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2024 Commandcracker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from textual.reactive import reactive
from textual.screen import ModalScreen

# built-in modules
from asyncio import gather
from shutil import which
from time import sleep, time
from typing import Union
from subprocess import Popen, PIPE
from os import name as os_name
import sys

# pip modules
# import mpv
# import ytdl
from textual import events, on, work
from random import choice
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal, ScrollableContainer
from textual.widgets import (Button, Checkbox, DataTable, Footer, Header,
                             Input, Label, ListItem, ListView, Markdown,
                             TabbedContent, TabPane)

from .provider.common import SearchResult, Series, Episode, Language
from .provider.aniworld import AniWorldProvider
from .provider.serienstream import SerienStreamProvider
from .player.common import Player
from .player.mpv import MPVPlayer
from .player.vlc import VLCPlayer
from .player.wmplayer import WMPlayer
from .player.ffplay import FFPlayPlayer
from .player.android import AndroidVLCPlayer, AndroidMPVPlayer, AndroidChoosePlayer
from .hoster.common import Hoster, DirectLink
from .hoster.veo import VOEHoster
from .hoster.vidoza import VidozaHoster
from .hoster.streamtape import StreamtapeHoster
from .hoster.doodstream import DoodstreamHoster
from .aniskip import (
    get_timings_from_search,
    timings_to_mpv_options,
    generate_chapters_file_and_get_mpv_option
)

__version__ = "1.0.0"

import logging
from pathlib import Path

logs_path = Path(__file__).parent.parent.parent.joinpath("logs")
logs_path.mkdir(exist_ok=True, parents=True)
logging.basicConfig(filename=logs_path.joinpath("anitui.log"), encoding='utf-8', level=logging.INFO)


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


class AniTUIApp(App):
    TITLE = "AniTUI"
    # TODO: color theme https://textual.textualize.io/guide/design/#designing-with-colors
    CSS_PATH = "anitui.tcss"

    def __init__(self):
        super().__init__()
        self.current: Union[list[SearchResult], None] = None
        self.current_info: Union[Series, None] = None

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Search", id="search"):  # Search "🔎"
                with Horizontal(id="hosters"):
                    yield Checkbox("AniWorld.to", True, id="aniworld_to")
                    yield Checkbox("SerienStream.to", id="serienstream_to")
                yield Input(id="input", placeholder="Search for a Anime")
                yield ListView(id="results")
            with TabPane("Info", id="info", disabled=True):  # Info "ℹ"
                with ScrollableContainer(id="res_con"):
                    yield Markdown(id="markdown")
                    yield ClickableDataTable(id="season_list")
            # with TabPane("Settings", id="setting"):  # Settings "⚙"
            #    yield Label("WIP")
            # with RadioSet():
            #    yield RadioButton("VOE", id="voe", value=True)
            #    yield RadioButton("Doodstream", id="doodstream")
            #    yield RadioButton("Vidoza", id="vidoza")
            #    yield RadioButton("Streamtape", id="streamtape")
        with Footer():
            with Center():
                yield Label("Made by Commandcracker with ❤")

    def on_mount(self) -> None:
        self.query_one(Input).focus()
        self.query_one("#info", TabPane).set_loading(True)
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        # TODO: make them scale
        table.add_columns("FT", "S", "F", "Name", "Title", "Hoster", "Sprache")
        if not which("mpv"):
            self.notify(
                "You wont be able to play videos directly.\n"
                "Please install MPV!",
                title="MPV not found",
                severity="warning",
            )

    async def on_checkbox_changed(self):
        self.lookup_anime(self.query_one("#input", Input).value)

    async def on_input_changed(self, message: Input.Changed) -> None:
        if message.value:
            self.lookup_anime(message.value)
        else:
            await self.query_one("#results", ListView).clear()

    # TODO: https://textual.textualize.io/guide/workers/#thread-workers
    @work(exclusive=True)
    async def lookup_anime(self, keyword: str) -> None:

        owos = []
        if self.query_one("#aniworld_to", Checkbox).value:
            owos.append(AniWorldProvider.search(keyword))

        if self.query_one("#serienstream_to", Checkbox).value:
            owos.append(SerienStreamProvider.search(keyword))

        lv = self.query_one("#results", ListView)
        await lv.clear()
        await lv.set_loading(True)
        results = await gather(*owos)
        f_results = []
        for l in results:
            if l is not None:
                for e in l:
                    f_results.append(e)

        # TODO: stor f_results by fuzzy sort keyword
        if len(f_results) > 0:
            self.current = f_results
            for series in f_results:
                await lv.append(ClickableListItem(Markdown(
                    f"##### **{series.name}** {series.production_year}\n{series.description}"
                )))
        await lv.set_loading(False)
        if len(f_results) > 0:
            lv.index = 0

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
            if key == "enter" and self.query_one(DataTable).has_focus:
                self.play_selected()

    def sort_favorite_lang(self, language_list: list[Language]) -> list[Language]:
        return sorted(language_list, key=lambda x: (
            x != Language.DE,
            x != Language.JP_DESUB,
            x != Language.JP_ENSUB,
        ))

    def sort_favorite_hoster(self, hoster_list: list[Hoster]) -> list[Hoster]:
        return sorted(hoster_list, key=lambda x: (
            not isinstance(x, VOEHoster),
            not isinstance(x, StreamtapeHoster),
            not isinstance(x, VidozaHoster),
            not isinstance(x, DoodstreamHoster),
        ))

    async def get_working_direct_link(self, hosters: list[Hoster]) -> Union[DirectLink, None]:
        for hoster in hosters:
            direct_link = await hoster.get_direct_link()
            is_working = await direct_link.check_is_working()
            logging.info('Check: "%s" Working: "%s" URL: "%s"', type(hoster).__name__, is_working, direct_link)
            if is_working:
                return direct_link
        return None

    @work(exclusive=True)
    async def play_selected(self):
        # TODO: cache more
        # TODO: dont only check for mpv
        #if which("mpv"):
        dt = self.query_one(DataTable)
        # TODO: show loading
        await dt.set_loading(True)
        index = self.app.query_one("#results", ListView).index
        series_search_result = self.current[index]
        self.play(
                series_search_result=series_search_result,
                fullscreen=True,
                episodes=self.current_info.episodes,
                index=dt.cursor_row
            )
        await dt.set_loading(False)
        #else:
        #    self.notify(
        #        "You wont be able to play videos directly.\n"
        #        "Please install MPV!",
        #        title="MPV not found",
        #        severity="error",
        #    )

    @work(exclusive=True)
    async def open_info(self) -> None:
        series_search_result: SearchResult = self.current[self.app.query_one("#results", ListView).index]
        info_tab = self.query_one("#info", TabPane)
        info_tab.disabled = False
        self.query_one(TabbedContent).active = "info"
        md = self.query_one("#markdown", Markdown)
        await info_tab.set_loading(True)
        series = await series_search_result.get_series()
        self.current_info = series
        await md.update(series.to_markdown())

        table = self.query_one(DataTable)
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
                if l == Language.DE:
                    ll.append("DE")
                if l == Language.JP_DESUB:
                    ll.append("JP_DESUB")
                if l == Language.JP_ENSUB:
                    ll.append("JP_ENSUB")

            c += 1
            table.add_row(
                c,
                ep.season,
                ep.episode_number,
                ep.title,
                "",
                ", ".join(hl),
                ", ".join(ll)
            )
        table.focus(scroll_visible=False)
        await info_tab.set_loading(False)

    def detect_player(self) -> Union[Player, None]:
        # Android
        if hasattr(sys, 'getandroidapilevel'):
            # TODO: detect right
            return AndroidMPVPlayer()
            #return AndroidVLCPlayer()
            #return AndroidChoosePlayer()
            #return None

        # All
        if which("mpv"):
            return MPVPlayer()
        if which("vlc"):
            return VLCPlayer()

        # Windows
        if os_name == "nt":
            if which(r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
                # r"C:\Program Files\VideoLAN\VLC\vlc.exe"
                return VLCPlayer()

        if which("ffplay"):
            return FFPlayPlayer()

        # Windows
        if os_name == "nt":
            return WMPlayer()

        return None

    @work(thread=True)
    async def play(
            self,
            series_search_result: SearchResult,
            fullscreen: bool,
            episodes: list[Episode],
            index: int
    ) -> None:
        episode: Episode = episodes[index]
        processed_hoster = await episode.process_hoster()

        lang = self.sort_favorite_lang(episode.available_language)[0]
        sorted_hoster = self.sort_favorite_hoster(processed_hoster.get(lang))
        direct_link = await self.get_working_direct_link(sorted_hoster)

        player = self.detect_player()

        if player is None:
            raise RuntimeError()

        # TODO: ani_skip, syncplay, fullscreen as arg
        # TODO: pass ani_skip as script
        ani_skip = True
        syncplay = True

        title = f"{series_search_result.name} - {episode.title}"

        path = None
        if isinstance(player, VLCPlayer):
            if not which("vlc"):
                if which(r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
                    path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

        args = player.play(direct_link.url, title, fullscreen, direct_link.headers, path)

        if isinstance(player, MPVPlayer):
            if ani_skip:
                timings = await get_timings_from_search(series_search_result.name, index + 1)
                if timings:
                    # --start=00:56
                    args += [
                        timings_to_mpv_options(timings),
                        generate_chapters_file_and_get_mpv_option(timings)
                    ]

        if syncplay:
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
                if isinstance(player, MPVPlayer) or isinstance(player, VLCPlayer):
                    # TODO: dont detect mpv.com
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
        process = Popen(
            args,
            stderr=PIPE
        )
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

                async def push_next_screen():
                    async def play_next(should_next):
                        if should_next:
                            self.play(
                                series_search_result,
                                fullscreen,
                                episodes,
                                index + 1,
                            )

                    await self.app.push_screen(Next("Playing next episode in", no_time=hasattr(sys, 'getandroidapilevel')), callback=play_next)

                self.app.call_later(push_next_screen)
                return


exit_quotes = [
    "Closing one anime is just an invitation to open another.",
    "You finished one, now finish the next.",
    "Don't stop now, there's a whole universe waiting to be explored.",
    "The end of one journey is just the beginning of another.",
    "Like a phoenix rising from the ashes, the end of one episode ignites the flames of anticipation for the next."
]


def main():
    anitui_app = AniTUIApp()
    anitui_app.run()
    print(choice(exit_quotes))


if __name__ == "__main__":
    main()
