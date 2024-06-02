"""
Clean Wordlist
==============

Given an input wordlist directory, cleans every list of words by removing invalid, non ASCII, non alpha words,
as well as inappropriate words as defined by the `ignored.txt` list.

"""

import argparse
from pathlib import Path
import shutil
import time
from typing import List, Set
from helpers import (
    is_letter,
    load_ignored_words,
)

# If True, updates the same input word list
# if False, creates a new file at the designated output location
UPDATE_IN_PLACE = True


def _clean(file: Path, ignored: Set[str] = set()) -> List[str]:
    """Cleans the specified file by removing non-alpha characters and excluding any words specified as ignored"""

    # Read all words from the input file
    with open(file, "r") as f:
        lines = f.readlines()
    # Remove words that contain non-alpha characters
    lines = list(filter(is_letter, lines))
    # Convert all words to lowercase
    lines = list(map(lambda w: w.lower(), lines))
    # Remove ignored words
    lines = list(filter(lambda w: w.strip() not in ignored, lines))
    # Ensure deterministic behavior later down the line
    lines.sort()

    return lines


def clean_wordlist(wordlist_dir: str, backup_original: bool = False) -> None:
    """Process all wordlists found in the specified directory"""

    # Load ignores
    ignored: Set[str] = set()
    ignored.update(load_ignored_words())

    # Find all files (individual wordlists) in the directory
    directory = Path(wordlist_dir)
    files = [f for f in directory.iterdir() if f.is_file()]

    # Process all files
    for file in files:
        # clean the file
        lines = _clean(file, ignored)

        # make a backup of the original file, if requested
        if backup_original:
            now = int(time.time())
            backup = f"{file}.{now}"
            shutil.copy(file, backup)
            print(f"Stored a backup at: {backup}")

        # update the original file
        with open(file, "w") as f:
            f.writelines(lines)
            print(f"Cleaned wordlist {file}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean all files found in a directory that represents a wordlist"
    )
    parser.add_argument("dir", help="Path to the directory.")
    args = parser.parse_args()

    clean_wordlist(args.dir)


if __name__ == "__main__":
    main()
