from asyncio import gather
from dataclasses import dataclass
from typing import Union

from bs4 import BeautifulSoup

from ..hoster.loadx import LoadXHoster
from ..networking import AcceptLanguage, AsyncClient
from ..hoster.veo import VOEHoster
from ..hoster.vidoza import VidozaHoster
from ..hoster.speedfiles import SpeedFilesHoster
from ..hoster.doodstream import DoodstreamHoster
from ..hoster.vidmoly import VidmolyHoster
from ..hoster.filemoon import FilemoonHoster
from ..hoster.luluvdo import LuluvdoHoster
from ..hoster.streamtape import StreamtapeHoster
from .common import Episode, Hoster, Language, Provider, SearchResult, Series
from ..utils import json_loads
from ..utils import fully_unescape

# TODO: Timeouts
# TODO: use base_url
# TODO: reuse same client
# TODO: do serienstream resolve using mounts (remove veryfy fale from hosts)


headers = {"Host": "serienstream.to"}
extensions = {"sni_hostname": "serienstream.to"}


def provider_to_hoster(provider: str, url: str) -> Hoster:
    if provider == "VOE":
        return VOEHoster(url)
    if provider == "Doodstream":
        return DoodstreamHoster(url)
    if provider == "Vidoza":
        return VidozaHoster(url)
    if provider == "Streamtape":
        return StreamtapeHoster(url)
    if provider == "SpeedFiles":
        return SpeedFilesHoster(url)
    if provider == "Filemoon":
        return FilemoonHoster(url)
    if provider == "Luluvdo":
        return LuluvdoHoster(url)
    if provider == "Vidmoly":
        return VidmolyHoster(url)
    if provider == "LoadX":
        return LoadXHoster(url)

def lang_img_src_lang_name_to_lang(name: str) -> Language:
    if name == "english":
        return Language.EN
    if name == "english-german":
        return Language.EN_DESUB
    if name == "japanese-english":
        return Language.JP_ENSUB
    if name == "japanese-german":
        return Language.JP_DESUB
    if name == "german":
        return Language.DE


@dataclass
class SerienStreamEpisode(Episode):
    url: str

    async def process_hoster(self) -> dict[Language, list[Hoster]]:
        async with AsyncClient(accept_language=AcceptLanguage.DE) as client:
            response = await client.get(
                f"{self.url}/staffel-{self.season}/episode-{self.episode_number}", headers=headers, extensions=extensions
            )
            soup = BeautifulSoup(response.text, "html.parser")
            watch_episode = soup.find_all(
                "li",
                class_=lambda value: value and value.startswith("episodeLink"),
                attrs={
                    "data-lang-key": True,
                    "data-link-id": True,
                    "data-link-target": True,
                    "data-external-embed": True,
                },
            )
            processed_hoster = {}
            for l in Language:
                processed_hoster[l] = list()

            langs = soup.find("div", class_="changeLanguage").find_all("img")
            lang_map = {}
            for lang in langs:
                lang_name = lang.attrs.get("src").split("/")[-1].rsplit(".", 1)[0]
                data_lang_key = lang.attrs.get("data-lang-key")
                lang_map[data_lang_key] = lang_img_src_lang_name_to_lang(lang_name)

            for episode in watch_episode:
                data_link_id = episode.attrs.get("data-link-id")
                provider = episode.find_next("h4").text

                data_lang_key = episode.attrs.get("data-lang-key")
                lang = lang_map[data_lang_key]

                hoster = provider_to_hoster(
                    provider,
                    f"https://{SerienStreamProvider.host}/redirect/{data_link_id}",
                )

                processed_hoster[lang].append(hoster)

            return processed_hoster


@dataclass
class SerienStreamSeries(Series):
    regisseure: set[str]
    schauspieler: set[str]
    produzent: set[str]
    land: list[str]
    full_description: str
    production_year: str
    tags: set[str]

    def to_markdown(self) -> str:
        string_builder = [f"# {self.name} {self.production_year}\n{self.full_description}\n\n"]
        if len(self.regisseure) > 0:
            string_builder.append(f"- **Regisseure**: {', '.join(self.regisseure)}\n")
        if len(self.schauspieler) > 0:
            string_builder.append(f"- **Schauspieler**: {', '.join(self.schauspieler)}\n")
        if len(self.produzent) > 0:
            string_builder.append(f"- **Produzent**: {', '.join(self.produzent)}\n")
        if len(self.land) > 0:
            string_builder.append(f"- **Land**: {', '.join(self.land)}\n")
        if len(self.tags) > 0:
            string_builder.append(f"- **Tags**: {', '.join(self.tags)}")
        return "".join(string_builder)


@dataclass
class SerienStreamSearchResult(SearchResult):
    link: str = None
    production_year: str = None
    host: str = None

    async def get_series(self) -> SerienStreamSeries:
        return await SerienStreamProvider.get_series(self)

    @property
    def url(self) -> str:
        return f"https://{self.host}/serie/stream/{self.link}"

    def __hash__(self):
        return super().__hash__()


@dataclass
class SerienStreamProvider(Provider):
    host: str = "186.2.175.5"

    @staticmethod
    async def search(keyword: str) -> Union[list[SerienStreamSearchResult], None]:
        if keyword.strip() == "":
            return None
        async with AsyncClient(accept_language=AcceptLanguage.DE) as client:
            response = await client.get(
                f"https://{SerienStreamProvider.host}/ajax/seriesSearch?keyword={keyword}", headers=headers, extensions=extensions
            )
            results = json_loads(response.content)
            search_results = []
            for series in results:
                search_results.append(
                    SerienStreamSearchResult(
                        provider_name="serienstream.to",
                        name=fully_unescape(series.get("name")).strip(),
                        link=series.get("link"),
                        description=fully_unescape(series.get("description")),
                        cover=f"https://s.to{series.get('cover')}",
                        production_year=series.get("productionYear"),
                        host=SerienStreamProvider.host,
                    )
                )
            return search_results

    @staticmethod
    async def get_series(search_result: SerienStreamSearchResult) -> SerienStreamSeries:
        async with AsyncClient(accept_language=AcceptLanguage.DE) as client:
            response = await client.get(search_result.url, headers=headers, extensions=extensions)
            soup = BeautifulSoup(response.text, "html.parser")

            tags = []
            for genre in soup.find_all(
                "a", class_="genreButton clearbutton", attrs={"itemprop": "genre"}
            ):
                tags.append(genre.text)

            actors = []
            for actor in soup.find_all("li", attrs={"itemprop": "actor"}):
                actors.append(actor.find_next("span", attrs={"itemprop": "name"}).text)

            creators = []
            for creator in soup.find_all("li", attrs={"itemprop": "creator"}):
                creators.append(
                    creator.find_next("span", attrs={"itemprop": "name"}).text
                )

            countrys = []
            for country in soup.find_all("li", attrs={"data-content-type": "country"}):
                countrys.append(
                    country.find_next("span", attrs={"itemprop": "name"}).text
                )

            directors = []
            for director in soup.find_all("li", attrs={"itemprop": "director"}):
                directors.append(
                    director.find_next("span", attrs={"itemprop": "name"}).text
                )

            funcs = []

            staffeln = (
                soup.find("div", attrs={"id": "stream"}, class_="hosterSiteDirectNav")
                .find("ul")
                .find_all("a")
            )
            count = 0
            for staffel in staffeln:
                # TODO: Filme
                if staffel.text != "Filme":
                    count += 1
                    if count > 1:
                        funcs.append(get_episodes_from_url(count, search_result.url))

            eps = await gather(
                get_episodes_from_soup(1, search_result.url, soup), *funcs
            )

            feps = []
            for e in eps:
                for b in e:
                    feps.append(b)

            return SerienStreamSeries(
                name=fully_unescape(
                    soup.find("h1", attrs={"itemprop": "name"}).find("span").text
                ).strip(),
                production_year=fully_unescape(
                    soup.find("div", class_="series-title").find("small").text
                ).strip(),
                # age=int(soup.find("div", class_="fsk").find("span").text),
                # imdb_link=soup.find("a", class_="imdb-link").attrs.get("href"),
                full_description=fully_unescape(
                    soup.find("p", class_="seri_des").attrs.get("data-full-description")
                ),
                regisseure=directors,
                schauspieler=actors,
                produzent=creators,
                land=countrys,
                tags=tags,
                # rating_value=int(soup.find("span", attrs={"itemprop": "ratingValue"}).text),
                # rating_count=int(soup.find("span", attrs={"itemprop": "ratingCount"}).text),
                # staffeln=count,
                episodes=feps,
                cover=f"https://{search_result.host}" + soup.find("img", attrs={"itemprop": "image"}).attrs.get("data-src")
            )


async def get_episodes_from_url(staffel: int, url: str) -> list[Episode]:
    async with AsyncClient(accept_language=AcceptLanguage.DE) as client:
        response = await client.get(f"{url}/staffel-{staffel}", headers=headers, extensions=extensions)
        return await get_episodes_from_page(staffel, url, response.text)


async def get_episodes_from_page(staffel: int, url: str, page: str) -> list[Episode]:
    return await get_episodes_from_soup(
        staffel, url, BeautifulSoup(page, "html.parser")
    )


async def get_episodes_from_soup(
    staffel: int, url: str, soup: BeautifulSoup
) -> list[Episode]:
    episodes = []
    e_count = 0
    for episode in (
        soup.find("table", class_="seasonEpisodesList").find("tbody").find_all("tr")
    ):
        title = episode.find_next("td", class_="seasonEpisodeTitle")

        language = set()
        for flag in episode.find_next("td", class_="editFunctions").find_all("img"):
            lang_name = flag.attrs.get("src").split("/")[-1].rsplit(".", 1)[0]
            language.add(lang_img_src_lang_name_to_lang(lang_name))

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
            if t == "SpeedFiles":
                hoster.add(SpeedFilesHoster)
            if t == "Filemoon":
                hoster.add(FilemoonHoster)
            if t == "Luluvdo":
                hoster.add(LuluvdoHoster)
            if t == "Vidmoly":
                hoster.add(VidmolyHoster)
            if t == "LoadX":
                hoster.add(LoadXHoster)

        e_count += 1
        title_en = fully_unescape(title.find("span").text.strip())
        title_de = fully_unescape(title.find("strong").text.strip())
        title = (
            f"{title_en} - {title_de}"
            if title_en and title_de
            else title_en or title_de
        )
        episodes.append(
            SerienStreamEpisode(
                url=url,
                title=title,
                season=staffel,
                episode_number=e_count,
                available_hoster=hoster,
                available_language=language,
                total_episode_number=None,
                # language=language,
                # hoster=hoster,
                # number=e_count,
                # staffel=staffel
            )
        )

    return episodes
