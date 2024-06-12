from tempfile import NamedTemporaryFile
from typing import Union
from dataclasses import dataclass

from fuzzywuzzy import process

from .networking import AsyncClient
from .tracker.myanimelist import search
from .rome import replace_roman_numerals
from .utils import json_loads


@dataclass
class SkipTimes:
    op_start: float
    op_end: float
    ed_start: float
    ed_end: float


async def get_timings_from_id(
    anime_id: int, episode_number: int
) -> Union[SkipTimes, None]:
    async with AsyncClient() as client:
        response = await client.get(
            f"https://api.aniskip.com/v1/skip-times/{anime_id}/{episode_number}?types=op&types=ed"
        )
        json = json_loads(response.content)
        if json.get("found") is not True:
            return
        op_start = 0
        op_end = 0
        ed_start = 0
        ed_end = 0
        for result in json["results"]:
            skip_type = result["skip_type"]
            start_time = result["interval"]["start_time"]
            end_time = result["interval"]["end_time"]
            if skip_type == "op":
                op_start = start_time
                op_end = end_time
            if skip_type == "ed":
                ed_start = start_time
                ed_end = end_time
        return SkipTimes(
            op_start=float(op_start),
            op_end=float(op_end),
            ed_start=float(ed_start),
            ed_end=float(ed_end)
        )


async def get_timings_from_search(
    keyword: str, episode_number: int
) -> Union[SkipTimes, None]:
    myanimelist_search_result = await search(keyword)
    animes = {}
    for anime in myanimelist_search_result["categories"][0]["items"]:
        animes[anime["id"]] = replace_roman_numerals(anime["name"])
    search_result = process.extractOne(replace_roman_numerals(keyword), animes, score_cutoff=50)
    if search_result is not None:
        anime_id = search_result[2]
        return await get_timings_from_id(anime_id, episode_number)
    return None


def chapter(start: float, end: float, title: str) -> str:
    return f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(start * 1000)}\nEND={int(end * 1000)}\nTITLE={title}\n"


def get_chapters_file_content(timings: SkipTimes) -> str:
    string_builder = [";FFMETADATA1"]
    if timings.op_start != timings.op_end:
        string_builder.append(chapter(timings.op_start, timings.op_end, "Opening"))
    if timings.ed_start != timings.ed_end:
        string_builder.append(chapter(timings.ed_start, timings.ed_end, "Ending"))
    if timings.op_end != 0 and timings.ed_start != 0:
        string_builder.append(chapter(timings.op_end, timings.ed_start, "Episode"))
    return "".join(string_builder)


def generate_chapters_file(timings: SkipTimes) -> NamedTemporaryFile:
    temp_file = NamedTemporaryFile(mode="w", prefix="gucken-", delete=False)
    temp_file.write(get_chapters_file_content(timings))
    temp_file.close()
    return temp_file
