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

# built-in modules
from abc import ABC, abstractmethod
import asyncio
from html import unescape
import re
from subprocess import Popen
from base64 import b64decode
from dataclasses import dataclass
from enum import Enum
from shutil import which
from time import time

# pip modules
# import mpv
# import ytdl
import httpx
from bs4 import BeautifulSoup
from rich import print
from textual.widgets._toggle_button import ToggleButton

from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Markdown,
    TabbedContent,
    TabPane,
    Checkbox,
)


@dataclass
class AniWorldSeriesSearchResult:
    name: str
    link: str
    short_description: str
    cover: str
    production_year: str


class Hoster(Enum):
    VOE = "VOE"
    DOODSTREAM = "Doodstream"
    VIDOZA = "Vidoza"
    STREAMTAPE = "Streamtape"


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


class Provider(ABC):
    @abstractmethod
    async def search(self, keyword: str) -> list[AniWorldSeriesSearchResult] | None:
        pass

    @abstractmethod
    async def get_info(self, link: str) -> AniWorldSeries | None:
        pass


async def search(keyword: str) -> list[AniWorldSeriesSearchResult] | None:
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"https://186.2.175.5/ajax/seriesSearch?keyword={keyword}")
        try:
            results = response.json()
            final = []
            for series in results:
                final.append(AniWorldSeriesSearchResult(
                    name=unescape(series['name']),
                    link=series['link'],
                    short_description=unescape(series['description']),
                    cover=series['cover'],
                    production_year=series['productionYear']
                ))
            return final
        except Exception:
            return None


async def get_veo_hls(url: str):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            url = soup.find("a", class_="watchEpisode").attrs.get("href")
            response = await client.get("https://186.2.175.5" + url, follow_redirects=True)

            match_hls = re.search(r"'hls': '(.*?)'", response.text)

            if match_hls:
                hls_link = match_hls.group(1)
            else:
                return None

            return b64decode(hls_link).decode()
        except Exception:
            return None


async def get_episodes_from_url(staffel: int, url: str) -> list[Episode]:
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        try:
            return await get_episodes_from_page(staffel, response.text)
        except Exception:
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


async def get_info(link: str) -> AniWorldSeries | None:
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(f"https://186.2.175.5/serie/stream/{link}")
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
                        funcs.append(get_episodes_from_url(count, f"https://186.2.175.5/serie/stream/{link}/staffel-{count}"))

            eps = await asyncio.gather(
                get_episodes_from_soup(1, soup),
                *funcs
            )

            feps = []
            for e in eps:
                for b in e:
                    feps.append(b)

            return AniWorldSeries(
                cover="https://186.2.175.5" + soup.find("div", class_="seriesCoverBox").find("img").attrs.get(
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


current = None

'''class CoolListView(ListView):
    def watch_index(self, old_index, new_index):
        if current is not None:
            if self._is_valid_index(old_index):
                series = current[old_index]
                child = self._nodes[old_index]
                assert isinstance(child, ListItem)
                try:
                    child.query_one(Markdown).update(
                        f"##### **{series.name}** {series.production_year}\n{series.short_description}")
                except NoMatches:
                    pass

            if self._is_valid_index(new_index):
                self.set_info(new_index)

        super().watch_index(old_index, new_index)

    @work(exclusive=True)
    async def set_info(self, index: int) -> None:
        series = current[index]
        url = f"https://186.2.175.5/serie/stream/{series.link}"

        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url)
            try:
                soup = BeautifulSoup(response.text, "html.parser")
                try:
                    full_description = unescape(
                        soup.find("p", class_="seri_des").attrs.get("data-full-description"))
                    child = self._nodes[index]
                    assert isinstance(child, ListItem)
                    try:
                        await child.query_one(Markdown).update(
                            f"##### **{series.name}** {series.production_year}\n{full_description}")
                    except NoMatches:
                        pass


                except AttributeError:
                    pass
            except Exception:
                pass'''


class ClickableListItem(ListItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_click = None

    def on_click(self) -> None:
        if self.last_click:
            if time() - self.last_click < 0.5:
                self.app.open_info(current[self.app.query_one("#results", ListView).index].link)
        self.last_click = time()


class AniTUIApp(App):
    TITLE = "AniTUI"

    def __init__(self):
        super().__init__()
        self.current = None
        self.current_info = None

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
                    yield DataTable()
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

    async def on_checkbox_changed(self, event: ToggleButton.Changed):
        if event.control.id == "aniworld_to":
            exit(event.value)

    async def on_input_changed(self, message: Input.Changed) -> None:
        if message.value:
            self.lookup_anime(message.value)
        else:
            await self.query_one("#results", ListView).clear()

    @work(exclusive=True)
    async def lookup_anime(self, keyword: str) -> None:
        lv = self.query_one("#results", ListView)
        await lv.clear()
        await lv.set_loading(True)
        results = await search(keyword)
        if results is not None:
            global current
            current = results
            for series in results:
                await lv.append(ClickableListItem(Markdown(
                    f"##### **{series.name}** {series.production_year}\n{series.short_description}"
                )))
        await lv.set_loading(False)
        if len(results) > 0:
            lv.index = 0

    # Aim assist :D
    async def on_key(self, event: events.Key) -> None:
        key = event.key
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
                    self.open_info(current[lv.index].link)
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
        dt = self.query_one(DataTable)
        ep: Episode = self.current_info.episodes[dt.cursor_row]
        await dt.set_loading(True)
        c = current[self.app.query_one("#results", ListView).index]
        hls = await get_veo_hls(f"https://186.2.175.5/serie/stream/{c.link}/staffel-{ep.staffel}/episode-{ep.number}")
        self.open_with_mpv(url=hls, title=f"{c.name} - {ep.title_de}", fullscreen=True)
        await dt.set_loading(False)

    @work(exclusive=True)
    async def open_info(self, link: str) -> None:
        info_tab = self.query_one("#info", TabPane)
        info_tab.disabled = False
        self.query_one(TabbedContent).active = "info"
        md = self.query_one("#markdown", Markdown)
        await info_tab.set_loading(True)
        info = await get_info(link)
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
    async def open_with_mpv(self, url: str, title: str, fullscreen: bool) -> None:
        p = Popen([
            "mpv",
            url,
            "--fullscreen" if fullscreen else "",
            f"--force-media-title={title}"
        ])
        while not self.app._exit:
            exit_code = p.poll()
            if exit_code is not None:
                # EXIT CODE 3 = Finished
                # EXIT CODE 0 = EXIT
                # exit(f"{exit_code} - NEXT")
                # Play Next
                return


def main():
    anitui_app = AniTUIApp()
    result = anitui_app.run()
    print(result)


if __name__ == "__main__":
    main()
