"""
Helpers
=======

Various helper functions and jazzy_fish_tools configurations.
"""

import itertools
import pkg_resources
from pathlib import Path
from queue import Queue
import shutil
from typing import Iterable, List, Tuple


MIN_LENGTH: int = 4
MAX_LENGTH: int = 8
MAX_PREFIX_CHARS: int = 6
OUTPUT_PATH: str = "out"
DATABASE: str = f"{OUTPUT_PATH}/dictionary.duckdb"


def least_similar_words(word_list: List[str], limit: int) -> List[str]:
    # Nothing to do if we have fewer words than the desired limit
    words = sorted(word_list)
    cnt = len(words)
    if cnt < limit:
        return words

    # Cannot really do much if only 2 words are available
    if cnt < 2:
        return words[:limit]

    results = list()
    # Start by selecting the first/last word, sorted alphabetically
    results += [words[0], words[cnt - 1]]

    q: Queue[Tuple[int, ...]] = Queue()

    # Build a balanced BST to attempt to randomize the chosen words
    q.put((1, cnt - 2))
    while not q.empty():
        el = q.get()
        if el[0] > el[1]:
            continue

        mid = (el[0] + el[1]) // 2
        results += [words[mid]]
        q.put((el[0], mid - 1))
        q.put((mid + 1, el[1]))

    return results[:limit]


# generate prefix combinations (MAX_CHARS, k) as the list of all possible prefix positions
# e.g., [0,1] will extract the first 2 letters of the word
# [0,2] will use the first and third letter
# etc.
def generate_all_prefix_combinations(of_length: int) -> List[Tuple[int, ...]]:
    # generate all combinations of prefixes of defined length
    elements: List[int] = list(range(0, MAX_PREFIX_CHARS))
    c = itertools.combinations(elements, of_length)
    return list(c)


def read_resource_lines(name: str) -> List[str]:
    """Reads data from a resource file within a package, split by lines."""
    data_path = pkg_resources.resource_filename(__name__, name)
    with open(data_path, "r") as file:
        data = file.readlines()
    return data


def read_resource(name: str) -> str:
    """Reads data from a resource file within a package."""
    data_path = pkg_resources.resource_filename(__name__, name)
    with open(data_path, "r") as file:
        data = file.read()
    return str(data)


def update_resource_lines(name: str, data: Iterable[str]) -> None:
    """Updates a resource file within a package."""
    data_path = pkg_resources.resource_filename(__name__, name)
    with open(data_path, "w") as file:
        file.writelines(data)


def reset_location(location: Path, remove_dir=True):
    """Remove any previously generated files near the location"""

    if remove_dir:
        try:
            # Remove any existing databases
            shutil.rmtree(location)
        except FileNotFoundError:
            pass

    # Ensure the output location exists
    location.mkdir(parents=True, exist_ok=True)


def load_ignored_words() -> List[str]:
    """Loads the list of ignored words"""
    ignore_file = "resources/ignored.txt"
    ignore_notice = "resources/ignored_NOTICE.txt"

    words = [
        w.strip()
        for w in read_resource_lines(ignore_file)
        if not w.strip().startswith("#") and w.strip()
    ]

    # Ensure the ignore list is itself clean
    if len(set(words)) != len(words):
        words = sorted(list(set(words)))
        notice = read_resource_lines(ignore_notice)
        update_resource_lines(ignore_file, notice + [f"{w}\n" for w in words])
        print(f"Cleaned ignore list {ignore_file}, updated in place")

    return words


def is_letter(word):
    """Returns true if the word contains only a-zA-Z letters"""
    return all(char.isascii() and char.isalpha() for char in word.strip())
