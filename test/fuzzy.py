import difflib
import logging
from difflib import SequenceMatcher

from rome import replace_roman_numerals
from textdistance import DamerauLevenshtein

levenshtein = DamerauLevenshtein()
import distance
from rapidfuzz import process

logging.basicConfig(level=logging.INFO)


def difflib_search(pattern, possibilities, threshold=0):
    matches = []
    for word in possibilities:
        ratio = SequenceMatcher(None, pattern, word).ratio()
        if ratio >= threshold:
            matches.append((word, ratio))
    return sorted(matches, key=lambda x: x[1], reverse=True)


def textdistance_search(pattern, possibilities, threshold=0, limit=5):
    matches = []
    for word in possibilities:
        ratio = levenshtein.normalized_similarity(pattern, word)
        if ratio >= threshold:
            matches.append((word, ratio))
    return sorted(matches, key=lambda x: x[1], reverse=True)


def distance_jaccard(pattern, possibilities, threshold=0, limit=5):
    matches = []
    for word in possibilities:
        ratio = distance.jaccard(pattern, word)
        if ratio >= threshold:
            matches.append((word, ratio))
    return sorted(matches, key=lambda x: x[1])


test_list = [
    "Overlord Movie 2: Shikkoku no Eiyuu",
    "Overlord",
    "Overlord IV",
    "Overlord III",
    "Overlord II",
    "Overlord: Ple Ple Pleiades - Nazarick Saidai no Kiki",
    "Overlord Movie 1: Fushisha no Ou",
    "Overlord: Ple Ple Pleiades",
    "Overlord Movie 3: Sei Oukoku-hen",
    "Overlord: Ple Ple Pleiades 2",
    "junk",
    "over junk",
    "very muxh over junk",
    "very muxh junk",
]

nl = []
for k in test_list:
    nl.append(replace_roman_numerals(k))

kw = replace_roman_numerals("Overlord II")

print("Query:", kw)
print("List:", nl)
print("")
print("rapidfuzz         ", process.extract(kw, nl, limit=100))
print("difflib           ", difflib_search(kw, nl))
print("textdistance      ", textdistance_search(kw, nl))
print("jaccard           ", distance_jaccard(kw, nl))
