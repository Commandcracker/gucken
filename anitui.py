#!/usr/bin/env python3
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

"""
WIP all kinda shitty code
"""

# built-in modules
from asyncio import gather
from base64 import b64decode
from dataclasses import dataclass
from enum import Enum
from html import unescape
from re import search as re_search
from shutil import which
from subprocess import Popen
from time import sleep, time

from bs4 import BeautifulSoup
# pip modules
# import mpv
# import ytdl
from httpx import AsyncClient
from rich import print
from textual import events, on, work
from textual.app import App, ComposeResult
from textual.containers import Center, Container, Horizontal
from textual.widgets import (Button, Checkbox, DataTable, Footer, Header,
                             Input, Label, ListItem, ListView, Markdown,
                             TabbedContent, TabPane)


@dataclass
class AniWorldSeriesSearchResult:
    name: str
    link: str
    short_description: str
    cover: str
    production_year: str
    host: str

    def get_url(self) -> str:
        if self.host == "186.2.175.5":
            return f"https://{self.host}/serie/stream/{self.link}"
        else:
            return f"https://{self.host}/anime/stream/{self.link}"


class Hoster(Enum):
    VOE = "VOE"
    DOODSTREAM = "Doodstream"
    VIDOZA = "Vidoza"
    STREAMTAPE = "Streamtape"


class VideoPlayer(Enum):
    VLC = "vlc"
    MPV = "mpv"
    WMPLAYER = "wmplayer"


class Language(Enum):
    DE = "Deutsch"
    JP_DESUB = "Japanisch mit deutschen untertitel"
    JP_ENSUB = "Japanisch mit englischen untertitel"


@dataclass
class Episode:
    title_en: str
    title_de: str | None
    language: set[Language]
    hoster: set[Hoster]
    number: int
    staffel: int


@dataclass
class AniWorldSeries:
    cover: str
    name: str
    production_year: str
    age: int
    imdb_link: str
    full_description: str
    regisseure: set[str]
    schauspieler: set[str]
    produzent: set[str]
    land: list[str]
    tags: set[str]
    rating_value: int
    rating_count: int
    staffeln: int
    episodes: list[Episode]
    # filme


async def search(host: str, keyword: str) -> list[AniWorldSeriesSearchResult] | None:
    if keyword.strip() == "":
        return None
    async with AsyncClient(verify=False) as client:
        response = await client.get(f"https://{host}/ajax/seriesSearch?keyword={keyword}")
        try:
            results = response.json()
            final = []
            for series in results:
                final.append(AniWorldSeriesSearchResult(
                    name=unescape(series['name']),
                    link=series['link'],
                    short_description=unescape(series['description']),
                    cover=series['cover'],
                    production_year=series['productionYear'],
                    host=host
                ))
            return final
        except Exception as e:
            exit(e)
            return None


async def get_veo_hls(series_search_result: AniWorldSeriesSearchResult, staffel: int, episode: int):
    async with AsyncClient(verify=False) as client:
        response = await client.get(f"{series_search_result.get_url()}/staffel-{staffel}/episode-{episode}")
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            url = soup.find("a", class_="watchEpisode").attrs.get("href")
            response = await client.get(f"https://{series_search_result.host}" + url, follow_redirects=True)

            match_hls = re_search(r"'hls': '(.*?)'", response.text)

            if match_hls:
                hls_link = match_hls.group(1)
            else:
                return None

            return b64decode(hls_link).decode()
        except Exception as e:
            exit(e)
            return None


async def get_episodes_from_url(staffel: int, url: str) -> list[Episode]:
    async with AsyncClient(verify=False) as client:
        response = await client.get(url)
        try:
            return await get_episodes_from_page(staffel, response.text)
        except Exception as e:
            exit(e)
            return None


async def get_episodes_from_page(staffel: int, page: str) -> list[Episode]:
    return await get_episodes_from_soup(staffel, BeautifulSoup(page, "html.parser"))


async def get_episodes_from_soup(staffel: int, soup: BeautifulSoup) -> list[Episode]:
    episodes = []
    e_count = 0
    for episode in soup.find("table", class_="seasonEpisodesList").find("tbody").find_all("tr"):
        title = episode.find_next("td", class_="seasonEpisodeTitle")

        language = set()
        for flag in episode.find_next("td", class_="editFunctions").find_all("img"):
            t = flag.attrs.get("title")
            if t == "Englisch":
                language.add(Language.JP_ENSUB)
            if t == "Deutsch/German":
                language.add(Language.DE)
            if t == "Mit deutschem Untertitel":
                language.add(Language.JP_DESUB)

        hoster = set()
        for h in episode.find_all_next("i", class_="icon"):
            t = h.attrs.get("title")
            if t == "VOE":
                hoster.add(Hoster.VOE)
            if t == "Doodstream":
                hoster.add(Hoster.DOODSTREAM)
            if t == "Vidoza":
                hoster.add(Hoster.VIDOZA)
            if t == "Streamtape":
                hoster.add(Hoster.STREAMTAPE)

        e_count += 1
        episodes.append(Episode(
            title_en=title.find("span").text.lstrip(),
            title_de=title.find("strong").text.lstrip(),
            language=language,
            hoster=hoster,
            number=e_count,
            staffel=staffel
        ))

    return episodes


async def get_info(series_search_result: AniWorldSeriesSearchResult) -> AniWorldSeries | None:
    async with AsyncClient(verify=False) as client:
        response = await client.get(series_search_result.get_url())
        try:
            soup = BeautifulSoup(response.text, "html.parser")

            tags = []
            for genre in soup.find_all("a", class_="genreButton clearbutton", attrs={"itemprop": "genre"}):
                tags.append(genre.text)

            actors = []
            for actor in soup.find_all("li", attrs={"itemprop": "actor"}):
                actors.append(actor.find_next("span", attrs={"itemprop": "name"}).text)

            creators = []
            for creator in soup.find_all("li", attrs={"itemprop": "creator"}):
                creators.append(creator.find_next("span", attrs={"itemprop": "name"}).text)

            countrys = []
            for country in soup.find_all("li", attrs={"data-content-type": "country"}):
                countrys.append(country.find_next("span", attrs={"itemprop": "name"}).text)

            directors = []
            for director in soup.find_all("li", attrs={"itemprop": "director"}):
                directors.append(director.find_next("span", attrs={"itemprop": "name"}).text)

            funcs = []

            staffeln = soup.find("div", attrs={"id": "stream"}, class_="hosterSiteDirectNav").find("ul").find_all("a")
            count = 0
            for staffel in staffeln:
                if staffel.text != "Filme":
                    count += 1
                    if count > 1:
                        funcs.append(
                            get_episodes_from_url(count, f"{series_search_result.get_url()}/staffel-{count}"))

            eps = await gather(
                get_episodes_from_soup(1, soup),
                *funcs
            )

            feps = []
            for e in eps:
                for b in e:
                    feps.append(b)

            return AniWorldSeries(
                cover=f"https://{series_search_result.host}" + soup.find("div", class_="seriesCoverBox").find(
                    "img").attrs.get(
                    "data-src"),
                name=unescape(soup.find("h1", attrs={"itemprop": "name"}).find("span").text),
                production_year=unescape(soup.find("div", class_="series-title").find("small").text).lstrip(),
                age=int(soup.find("div", class_="fsk").find("span").text),
                imdb_link=soup.find("a", class_="imdb-link").attrs.get("href"),
                full_description=unescape(soup.find("p", class_="seri_des").attrs.get("data-full-description")),
                regisseure=directors,
                schauspieler=actors,
                produzent=creators,
                land=countrys,
                tags=tags,
                rating_value=int(soup.find("span", attrs={"itemprop": "ratingValue"}).text),
                rating_count=int(soup.find("span", attrs={"itemprop": "ratingCount"}).text),
                staffeln=count,
                episodes=feps
            )
        except Exception as e:
            exit(e)
            return None


class Next(ModalScreen):
    time = reactive(3)

    def __init__(self, question):
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(self.question)
            with Horizontal():
                yield Button.error("Cancel", id="cancel")
                yield Button.success("Next", id="next")

    def on_mount(self) -> None:
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


def play_with_mpv(url: str, title: str, fullscreen: bool, path: str = "mpv") -> Popen:
    return Popen([
        path,
        url,
        "--fullscreen" if fullscreen else "",
        f"--force-media-title={title}"
    ])


def play_with_vlc(url: str, title: str, fullscreen: bool, path: str = "vlc") -> Popen:
    return Popen([
        path,
        url,
        "--no-video-title-show",
        "--fullscreen" if fullscreen else "",
        f"--input-title-format={title}"
    ])


def play_with_wmplayer(
        url: str,
        title: str,
        fullscreen: bool,
        path: str = r"C:\Program Files (x86)\Windows Media Player\wmplayer.exe"
) -> Popen:
    return Popen([
        path,
        url,
        "/fullscreen" if fullscreen else "",
    ])


class AniTUIApp(App):
    TITLE = "AniTUI"
    CSS = """
    Next {
        align: center middle;
    }
    
    Next > Container {
        width: auto;
        height: auto;
        align: center middle;
        padding: 1 2;
        background: $panel;
    }
    
    Next > Container > Label {
        width: 100%;
        content-align-horizontal: center;
    }
    
    Next > Container > Horizontal {
        height: auto;
        width: auto;
    }
    
    Next > Container > Horizontal > Button {
        margin: 1 2;
    }
    """

    def __init__(self):
        super().__init__()
        self.current: list[AniWorldSeriesSearchResult] | None = None
        self.current_info: AniWorldSeries | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Search", id="search"):
                yield Checkbox("AniWorld.to", True, id="aniworld_to")
                yield Checkbox("S.to", id="s_to")
                yield Input(id="input", placeholder="Search for a Anime")
                yield ListView(id="results")
            with TabPane("Info", id="info", disabled=True):
                yield Markdown(id="markdown")
                with Horizontal():
                    yield ClickableDataTable()
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
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Folge", "Staffel", "Folge", "Name", "Title", "Hoster", "Sprache")
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

    @work(exclusive=True)
    async def lookup_anime(self, keyword: str) -> None:

        owos = []
        if self.query_one("#aniworld_to", Checkbox).value:
            owos.append(search("aniworld.to", keyword))

        if self.query_one("#s_to", Checkbox).value:
            owos.append(search("186.2.175.5", keyword))

        lv = self.query_one("#results", ListView)
        await lv.clear()
        await lv.set_loading(True)
        results = await gather(*owos)
        f_results = []
        for l in results:
            if l is not None:
                for e in l:
                    f_results.append(e)

        if len(f_results) > 0:
            self.current = f_results
            for series in f_results:
                await lv.append(ClickableListItem(Markdown(
                    f"##### **{series.name}** {series.production_year}\n{series.short_description}"
                )))
        await lv.set_loading(False)
        if len(f_results) > 0:
            lv.index = 0

    # Aim assist :D
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

    @work(exclusive=True)
    async def play_selected(self):
        if which("mpv"):
            dt = self.query_one(DataTable)
            ep: Episode = self.current_info.episodes[dt.cursor_row]
            await dt.set_loading(True)
            index = self.app.query_one("#results", ListView).index
            c = self.current[index]
            hls = await get_veo_hls(c, ep.staffel, ep.number)
            # TODO: Check if hls link is 404
            self.play(
                url=hls,
                series_search_result=c,
                fullscreen=True,
                episodes=self.current_info.episodes,
                index=dt.cursor_row
            )
            await dt.set_loading(False)
        else:
            self.notify(
                "You wont be able to play videos directly.\n"
                "Please install MPV!",
                title="MPV not found",
                severity="error",
            )

    @work(exclusive=True)
    async def open_info(self) -> None:
        series_search_result: AniWorldSeriesSearchResult = self.current[self.app.query_one("#results", ListView).index]
        info_tab = self.query_one("#info", TabPane)
        info_tab.disabled = False
        self.query_one(TabbedContent).active = "info"
        md = self.query_one("#markdown", Markdown)
        await info_tab.set_loading(True)
        info = await get_info(series_search_result)
        self.current_info = info
        await md.update(f"# {info.name} {info.production_year}\n{info.full_description}\n\n"
                        f"**Regisseure**: {', '.join(info.regisseure)}\\\n"
                        f"**Schauspieler**: {', '.join(info.schauspieler)}\\\n"
                        f"**Produzent**: {', '.join(info.produzent)}\\\n"
                        f"**Land**: {', '.join(info.land)}\n\n"
                        f"**Tags**: {', '.join(info.tags)}")

        table = self.query_one(DataTable)
        table.clear()
        c = 0
        for ep in info.episodes:
            hl = []
            for h in ep.hoster:
                if h == Hoster.VOE:
                    hl.append("VEO")
                if h == Hoster.DOODSTREAM:
                    hl.append("D")
                if h == Hoster.VIDOZA:
                    hl.append("VZ")
                if h == Hoster.STREAMTAPE:
                    hl.append("ST")

            ll = []
            for l in ep.language:
                if l == Language.DE:
                    ll.append("DE")
                if l == Language.JP_DESUB:
                    ll.append("JP_DESUB")
                if l == Language.JP_ENSUB:
                    ll.append("JP_ENSUB")

            c += 1
            table.add_row(
                c,
                ep.staffel,
                ep.number,
                ep.title_de,
                ep.title_en,
                ", ".join(hl),
                ", ".join(ll)
            )
        table.focus()
        await info_tab.set_loading(False)

    @work(thread=True)
    async def play(
            self,
            url: str,
            series_search_result: AniWorldSeriesSearchResult,
            fullscreen: bool,
            episodes: list[Episode],
            index: int
    ) -> None:

        player = VideoPlayer.MPV
        ep: Episode = episodes[index]
        title = f"{series_search_result.name} - {ep.title_de}"

        if player == VideoPlayer.MPV:
            p = play_with_mpv(url, title, fullscreen)
        if player == VideoPlayer.VLC:
            path = "vlc"
            if not which("vlc"):
                if which(r"C:\Program Files\VideoLAN\VLC\vlc.exe"):
                    path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"

            p = play_with_vlc(url, title, fullscreen, path)
        if player == VideoPlayer.WMPLAYER:
            p = play_with_wmplayer(url, title, fullscreen)

        while not self.app._exit:
            sleep(0.5)
            exit_code = p.poll()
            # EXIT CODE 3 = Finished Video
            # EXIT CODE 0 = EXIT
            if exit_code is not None:
                async def push_next_screen():
                    async def play_next(should_next):
                        if should_next:
                            episode: Episode = episodes[index + 1]
                            hls = await get_veo_hls(series_search_result, episode.staffel, episode.number)
                            self.play(hls, series_search_result, fullscreen, episodes, index + 1)

                    await self.app.push_screen(Next("Playing next episode in"), callback=play_next)

                self.app.call_later(push_next_screen)
                return


def main():
    anitui_app = AniTUIApp()
    anitui_app.run()
    print("Good bye!")


if __name__ == "__main__":
    main()
