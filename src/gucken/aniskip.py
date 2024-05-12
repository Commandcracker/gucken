from difflib import SequenceMatcher
from tempfile import NamedTemporaryFile
from typing import Union

from httpx import AsyncClient

from .tracker.myanimelist import search


# TODO: improve fuzzy

def fuzzy_search(pattern, possibilities, threshold=0.6):
    matches = []
    for word in possibilities:
        ratio = SequenceMatcher(None, pattern, word).ratio()
        if ratio >= threshold:
            matches.append((word, ratio))
    return matches


def fuzzy_sort(pattern, possibilities):
    return sorted(possibilities, key=lambda x: SequenceMatcher(None, pattern, x).ratio(), reverse=True)


async def get_timings_from_id(anime_id: int, episode_number: int) -> Union[dict[str, float], None]:
    async with AsyncClient(verify=False) as client:
        response = await client.get(
            f"https://api.aniskip.com/v1/skip-times/{anime_id}/{episode_number}?types=op&types=ed"
        )
        json = response.json()
        if json.get("found") is not True:
            return None
        op_start_time = 0
        op_end_time = 0
        ed_start_time = 0
        ed_end_time = 0
        for result in json["results"]:
            skip_type = result["skip_type"]
            start_time = result["interval"]["start_time"]
            end_time = result["interval"]["end_time"]
            if skip_type == "op":
                op_start_time = start_time
                op_end_time = end_time
            if skip_type == "ed":
                ed_start_time = start_time
                ed_end_time = end_time
        return {
            "op_start_time": float(op_start_time),
            "op_end_time": float(op_end_time),
            "ed_start_time": float(ed_start_time),
            "ed_end_time": float(ed_end_time)
        }


async def get_timings_from_search(keyword: str, episode_number: int) -> Union[dict[str, float], None]:
    # TODO: improve search
    myanimelist_search_result = await search(keyword)
    animes = {}
    for anime in myanimelist_search_result["categories"][0]["items"]:
        animes[anime["name"]] = anime["id"]
    search_results = fuzzy_search(keyword, animes)
    if len(search_results) > 0:
        name = search_results[0][0]
        anime_id = animes[name]
        return await get_timings_from_id(anime_id, episode_number)
    return None


def timings_to_mpv_options(timings=dict[str, float]) -> str:
    op_start_time = timings["op_start_time"]
    op_end_time = timings["op_end_time"]
    ed_start_time = timings["ed_start_time"]
    ed_end_time = timings["ed_end_time"]
    return f"--script-opts=skip-op_start={op_start_time},skip-op_end={op_end_time},skip-ed_start={ed_start_time},skip-ed_end={ed_end_time}"


def chapter(start: float, end: float, title: str) -> str:
    return f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={int(start * 1000)}\nEND={int(end * 1000)}\nTITLE={title}\n"


def get_chapters_file_content(timings=dict[str, float]) -> str:
    op_start_time = timings["op_start_time"]
    op_end_time = timings["op_end_time"]
    ed_start_time = timings["ed_start_time"]
    ed_end_time = timings["ed_end_time"]
    return (
            ";FFMETADATA1" +
            chapter(op_start_time, op_end_time, "Opening") +
            chapter(ed_start_time, ed_end_time, "Ending") +
            chapter(op_end_time, ed_start_time, "Episode")
    )


def generate_chapters_file(timings=dict[str, float]) -> NamedTemporaryFile:
    temp_file = NamedTemporaryFile(mode='w', prefix="gucken-", delete=False)
    temp_file.write(get_chapters_file_content(timings))
    temp_file.close()
    return temp_file


def get_chapters_file_mpv_option(path: str) -> str:
    return f"--chapters-file={path}"
