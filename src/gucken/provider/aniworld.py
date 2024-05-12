from asyncio import gather
from dataclasses import dataclass
from html import unescape
from typing import Union

from bs4 import BeautifulSoup
from httpx import AsyncClient

from ..hoster.doodstream import DoodstreamHoster
from ..hoster.streamtape import StreamtapeHoster
from ..hoster.veo import VOEHoster
from ..hoster.vidoza import VidozaHoster
from .common import Episode, Hoster, Language, Provider, SearchResult, Series


def data_lang_key_to_lang(data_lang_key: str) -> Language:
    if data_lang_key == "1":
        return Language.DE
    if data_lang_key == "2":
        return Language.JP_ENSUB
    if data_lang_key == "3":
        return Language.JP_DESUB


def provider_to_hoster(provider: str, url: str) -> Hoster:
    if provider == "VOE":
        return VOEHoster(url)
    if provider == "Doodstream":
        return DoodstreamHoster(url)
    if provider == "Vidoza":
        return VidozaHoster(url)
    if provider == "Streamtape":
        return StreamtapeHoster(url)


@dataclass
class AniWorldEpisode(Episode):
    url: str

    async def process_hoster(self) -> dict[Language, list[Hoster]]:
        async with AsyncClient(verify=False) as client:
            response = await client.get(f"{self.url}/staffel-{self.season}/episode-{self.episode_number}")
            soup = BeautifulSoup(response.text, "html.parser")
            watch_episode = soup.find_all(
                "li",
                class_=lambda value: value and value.startswith("episodeLink"),
                attrs={
                    "data-lang-key": True,
                    "data-link-id": True,
                    "data-link-target": True,
                    "data-external-embed": True
                }
            )

            processed_hoster = {
                Language.DE: list(),
                Language.JP_DESUB: list(),
                Language.JP_ENSUB: list(),
            }

            for episode in watch_episode:
                data_link_id = episode.attrs.get("data-link-id")
                provider = episode.find_next("h4").text

                data_lang_key = episode.attrs.get("data-lang-key")
                lang = data_lang_key_to_lang(data_lang_key)

                hoster = provider_to_hoster(provider, f"https://{AniWorldProvider.host}/redirect/{data_link_id}")

                processed_hoster[lang].append(hoster)

            return processed_hoster


@dataclass
class AniWorldSeries(Series):
    regisseure: set[str]
    schauspieler: set[str]
    produzent: set[str]
    land: list[str]
    full_description: str
    production_year: str
    tags: set[str]

    def to_markdown(self) -> str:
        return (
            f"# {self.name} {self.production_year}\n{self.full_description}\n\n"
            f"**Regisseure**: {', '.join(self.regisseure)}\\\n"
            f"**Schauspieler**: {', '.join(self.schauspieler)}\\\n"
            f"**Produzent**: {', '.join(self.produzent)}\\\n"
            f"**Land**: {', '.join(self.land)}\n\n"
            f"**Tags**: {', '.join(self.tags)}"
        )


@dataclass
class AniWorldSearchResult(SearchResult):
    link: str = None
    production_year: str = None
    host: str = None

    async def get_series(self) -> AniWorldSeries:
        return await AniWorldProvider.get_series(self)

    @property
    def url(self) -> str:
        return f"https://{self.host}/anime/stream/{self.link}"


@dataclass
class AniWorldProvider(Provider):
    host = "aniworld.to"

    @staticmethod
    async def search(keyword: str) -> Union[list[AniWorldSearchResult], None]:
        if keyword.strip() == "":
            return None
        async with AsyncClient(verify=False) as client:
            response = await client.get(f"https://{AniWorldProvider.host}/ajax/seriesSearch?keyword={keyword}")
            results = response.json()
            search_results = []
            for series in results:
                search_results.append(AniWorldSearchResult(
                    name=unescape(series.get("name")),
                    link=series.get("link"),
                    description=unescape(series.get("description")),
                    cover=f"https://{AniWorldProvider.host}{series.get('cover')}",
                    production_year=series.get("productionYear"),
                    host=AniWorldProvider.host
                ))
            return search_results

    @staticmethod
    async def get_series(search_result: AniWorldSearchResult) -> AniWorldSeries:
        async with (AsyncClient(verify=False) as client):
            response = await client.get(search_result.url)
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
                # TODO: Filme
                if staffel.text != "Filme":
                    count += 1
                    if count > 1:
                        funcs.append(
                            get_episodes_from_url(count, search_result.url))

            eps = await gather(
                get_episodes_from_soup(1, search_result.url, soup),
                *funcs
            )

            feps = []
            for e in eps:
                for b in e:
                    feps.append(b)

            return AniWorldSeries(
                # cover=f"https://{search_result.host}" + soup.find("div", class_="seriesCoverBox").find("img").attrs.get("data-src"),
                name=unescape(soup.find("h1", attrs={"itemprop": "name"}).find("span").text),
                production_year=unescape(soup.find("div", class_="series-title").find("small").text).lstrip(),
                # age=int(soup.find("div", class_="fsk").find("span").text),
                # imdb_link=soup.find("a", class_="imdb-link").attrs.get("href"),
                full_description=unescape(soup.find("p", class_="seri_des").attrs.get("data-full-description")),
                regisseure=directors,
                schauspieler=actors,
                produzent=creators,
                land=countrys,
                tags=tags,
                # rating_value=int(soup.find("span", attrs={"itemprop": "ratingValue"}).text),
                # rating_count=int(soup.find("span", attrs={"itemprop": "ratingCount"}).text),
                # staffeln=count,
                episodes=feps
            )


async def get_episodes_from_url(staffel: int, url: str) -> list[Episode]:
    async with AsyncClient(verify=False) as client:
        response = await client.get(f"{url}/staffel-{staffel}")
        return await get_episodes_from_page(staffel, url, response.text)


async def get_episodes_from_page(staffel: int, url: str, page: str) -> list[Episode]:
    return await get_episodes_from_soup(staffel, url, BeautifulSoup(page, "html.parser"))


async def get_episodes_from_soup(staffel: int, url: str, soup: BeautifulSoup) -> list[Episode]:
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
                hoster.add(VOEHoster)
            if t == "Doodstream":
                hoster.add(DoodstreamHoster)
            if t == "Vidoza":
                hoster.add(VidozaHoster)
            if t == "Streamtape":
                hoster.add(StreamtapeHoster)

        e_count += 1
        title_en = title.find("span").text.lstrip()
        title_de = title.find("strong").text.lstrip()
        episodes.append(AniWorldEpisode(
            url=url,
            title=f"{title_en} - {title_de}",
            season=staffel,
            episode_number=e_count,
            available_hoster=hoster,
            available_language=language,
            total_episode_number=None
            # language=language,
            # hoster=hoster,
            # number=e_count,
            # staffel=staffel
        ))

    return episodes