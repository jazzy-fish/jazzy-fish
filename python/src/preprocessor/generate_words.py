"""
Generate Words
==============

Generates combinations of words, prefix lengths, and word sequences to help the user choose the best configuration
for their use-case.

"""

import argparse
from functools import reduce
from preprocessor.helpers import sha1, agg_sha1
from pathlib import Path
import random
from encoder.encoder import WordEncoder
import time
from typing import List, Set, Tuple
from preprocessor.helpers import (
    DATABASE,
    MAX_LENGTH,
    MIN_LENGTH,
    OUTPUT_PATH,
    generate_all_prefix_combinations,
    load_ignored_words,
    least_similar_words,
    read_resource,
    reset_location,
)
import duckdb
from duckdb.typing import VARCHAR, INTEGER

# Set to true to only analyze real prefixes (01, 012, 0123, etc.)
ONLY_SEQ_PREFIXES = True

# Defines the prefix length variations to consider when generating combinations
PREFIX_LENGTHS: Tuple[int, ...] = (2, 3, 4, 5, 6)

# The allowed word parts that must match file names in a wordlist directory
ALLOWED_WORD_PARTS: Tuple[str, ...] = ("adverb", "adjective", "verb", "noun")


def initialize_database() -> duckdb.DuckDBPyConnection:
    """Reinitialize the database, tables, and UDFs"""

    conn = duckdb.connect(database=DATABASE)

    conn.create_function(
        "least_similar_words",
        least_similar_words,
        parameters=[duckdb.list_type(VARCHAR), INTEGER],
        return_type=duckdb.list_type(VARCHAR),
        type="native",
    )

    return conn


def categorize_words(
    conn: duckdb.DuckDBPyConnection,
    wordlist: Path,
    char_positions: Tuple[int, ...],
    is_prefix: bool,
    seen_words: Set[str],
):
    position_in_word = "".join(map(str, char_positions))

    results = list()

    # Read all words in word list
    with open(wordlist, "r") as file:
        # Ensure the file is named correctly
        word_part = Path(wordlist).stem
        if word_part not in ALLOWED_WORD_PARTS:
            raise ValueError(
                f"All files in a wordlist dir must match one of the ALLOWED_WORD_PARTS; {word_part} is invalid"
            )

        # Read all words in file
        for line in file:
            # Remove extraneous characters (i.e., '\n')
            word = line.strip()

            # Respect word sizes
            if len(word) < MIN_LENGTH or len(word) > MAX_LENGTH:
                continue

            # Skip words that were already seen
            # to avoid generating sentences of the same token
            if word in seen_words:
                continue
            seen_words.add(word)

            # Skip words shorter than the required prefix position
            if len(word) <= char_positions[-1]:
                continue

            # Compute the actual prefix
            prefix_chars = "".join([word[p] for p in char_positions])

            # Define the fields to persist
            fields = [
                len(position_in_word),  # prefix length
                position_in_word,
                is_prefix,  # if the prefix is a true prefix starting with the first char (012,etc) or a non contiguous seq
                prefix_chars,
                word,
                word_part,
            ]

            # Prepare for insertion to the database
            quoted = [f"'{item}'" if isinstance(item, str) else item for item in fields]

            # Append the entry
            results.append(",".join(map(str, quoted)))

    # Store words in batches
    sz = 1000
    batches = [(boundary, boundary + sz) for boundary in range(0, len(results), sz)]
    for b in batches:
        # Store the result set into the database
        start, finish = b
        batch = results[start:finish]
        values = "), (".join(batch)
        sql = f"INSERT INTO words VALUES ({values});"
        conn.execute(sql)


def main() -> None:
    # Define the input wordlist
    parser = argparse.ArgumentParser(
        description="Specify the directory that holds the relevant input wordlists"
    )
    parser.add_argument("dir", help="Path to the directory.")
    args = parser.parse_args()

    # Clean any previous results
    reset_location(Path(DATABASE).parent)

    # This function uses DuckDB to store the analyzed words/prefixes.
    # Initialize a new DuckDB database
    conn = initialize_database()

    # Re/create the table structure for holding interim data
    conn.execute(read_resource("resources/process/ct_words.sql"))

    print("Processing word lists...")
    start_time = time.time()
    for prefix_length in PREFIX_LENGTHS:
        for char_positions in generate_all_prefix_combinations(prefix_length):
            # Skip non-sequential prefixes, if needed
            is_prefix = char_positions == tuple(range(0, prefix_length))
            if ONLY_SEQ_PREFIXES and not is_prefix:
                continue

            print(f"Processing {char_positions}")

            # Avoid duplicate words and also globally exclude ignored words
            seen_words: Set[str] = set()
            seen_words.update(load_ignored_words())

            # Find all files (individual wordlists) in the directory
            directory = Path(args.dir)
            files = [f for f in directory.iterdir() if f.is_file()]
            for file in files:
                categorize_words(conn, file, char_positions, is_prefix, seen_words)

        end_time = time.time()
        print(f"Processed word lists in: {end_time - start_time:.2f} seconds\n")

        # Process the words table and extract words for each prefix
        print("Extracting unique words, grouped by prefix...")
        sql = read_resource("resources/process/process_words.sql")
        conn.execute(sql)
        print("Unique words extracted. (TABLE `words_by_prefix`)")

    print("Generating final word lists...")
    reset_location(Path(f"{OUTPUT_PATH}/processed"))

    for prefix_length in PREFIX_LENGTHS:
        for char_positions in generate_all_prefix_combinations(prefix_length):
            # Skip non-sequential prefixes, if needed
            is_prefix = char_positions == tuple(range(0, prefix_length))
            if ONLY_SEQ_PREFIXES and not is_prefix:
                continue

            position_in_word = "".join([str(c) for c in char_positions])

            # Generate an output location for the current wordlist and ensure it exists
            wordlist_out_dir = f"{OUTPUT_PATH}/processed/{position_in_word}"
            reset_location(Path(wordlist_out_dir), remove_dir=False)

            wordlists: List[str] = list()
            stats: List[Tuple[str, int]] = list()

            # Note: this code assumes that the four word parts are always specified and will only process these, not other names
            for word_part in ALLOWED_WORD_PARTS:
                # Skip non-sequential prefixes, if needed
                is_prefix = char_positions == tuple(range(0, prefix_length))
                if ONLY_SEQ_PREFIXES and not is_prefix:
                    continue

                word_size = f"[{MIN_LENGTH}, {MAX_LENGTH}]"
                print(
                    f"Generating {position_in_word}, word type '{word_part}', word length {word_size}..."
                )

                sql = f"""SELECT selected_words[1] AS word
                          FROM words_by_prefix
                          WHERE position = '{position_in_word}'
                                AND word_part = '{word_part}'
                          ORDER BY 1;"""
                result = conn.execute(sql).fetchall()

                # Store the selected words
                outfile = f"{wordlist_out_dir}/{word_part}.txt"
                with open(outfile, "a") as out:
                    for row in result:
                        out.write(row[0] + "\n")
                print(f"Saved '{outfile}'\n")

                # Store the wordlists and stats
                wordlists.append(outfile)
                stats.append((word_part, len(result)))

            # Generate stats
            print(f"Storing stats for 2/3/4 words for {position_in_word}...\n")
            ordered = sorted(stats, key=lambda x: x[1])

            two_words = [f[0] for f in ordered[-2:]]
            _save_stats(conn, position_in_word, is_prefix, two_words, wordlists)

            three_words = [f[0] for f in ordered[-3:]]
            _save_stats(conn, position_in_word, is_prefix, three_words, wordlists)

            four_words = [f[0] for f in ordered]
            _save_stats(conn, position_in_word, is_prefix, four_words, wordlists)

            # Generate checksums
            checksums = list()
            for word in wordlists:
                name = Path(word).name
                checksum = sha1(word)
                line = f"{checksum}  {name}"

                # Store checksum and also generate separate checksum file
                checksums.append(line)
                with open(f"{Path(word)}.sha1", "w") as f:
                    f.write(line)
            checksums.sort()

            # The first checksum will represent the aggregate checksum for all wordlists
            outfile = f"{wordlist_out_dir}/checksums.sha1"
            agg_checksum = agg_sha1(checksums)
            with open(outfile, "w") as out:
                out.write(f"{agg_checksum}\n")
                for checksum in checksums:
                    out.write(f"{checksum}\n")

            # Rename the output wordlist to include part of the aggregated checksum
            renamed = f"{OUTPUT_PATH}/processed/{position_in_word}_{agg_checksum[:7]}"
            Path(wordlist_out_dir).rename(renamed)

    end_time = time.time()
    print(f"\nGenerated word lists in: {end_time - start_time:.2f} seconds")


def _save_stats(
    conn: duckdb.DuckDBPyConnection,
    position_in_word: str,
    is_prefix: bool,
    word_parts: List[str],
    wordlists: List[str],
):
    """Store statistics about the selected words"""

    parts = ", ".join([f"'{w}'" for w in word_parts])
    sql = f"""WITH
            prefix_stats AS (
                SELECT
                    position,
                    word_part,
                    COUNT(DISTINCT identifier) AS single_words_per_prefix,
                    SUM(max_words_for_prefix) AS total_words
                FROM
                    words_by_prefix
                WHERE
                    position = '{position_in_word}'
                    AND word_part IN ({parts})
                GROUP BY ALL
            ),
            total AS (
                SELECT
                    PRODUCT (single_words_per_prefix) AS total
                FROM
                    prefix_stats
                GROUP BY
                    ALL
            )
        SELECT
            position,
            word_part,
            single_words_per_prefix AS total
        FROM
            prefix_stats
        UNION ALL
        SELECT
            'Total',
            '',
            total
        FROM
            total;
    """
    result = conn.execute(sql).fetchall()

    def _r0(row: List[str]) -> str:
        return row[0] or ""

    data = [f"{_r0(row):10s} {row[1]:12s} {int(row[2] or 0):,d}\n" for row in result]

    outfile = f"{OUTPUT_PATH}/processed/{position_in_word}/stats_{len(word_parts)}.txt"
    with open(outfile, "w") as out:
        total = int(result[-1][2] or 0)
        years_s = total / 31536000
        years_ms = total / 31536000000

        t = "SEQ" if is_prefix else "RND"
        out.write(
            f"Result: [{years_s: 12,.0f} years at 1/s ] [{total: 22,.0f}] ({parts:42s}) for prefix: '{position_in_word:6s}' [{t}]\n\n"
            f"Result: [{years_ms: 12,.0f} years at 1/ms] [{total: 22,.0f}] ({parts:42s}) for prefix: '{position_in_word:6s}' [{t}]\n\n"
        )
        out.writelines(data)
        out.write(f"Years at 1/s            {years_s:,.2f}\n")
        out.write(f"Years at 1/ms           {years_ms:,.3f}\n")
        out.write("\n")
        out.write("Sample words:\n")

        words = _generate_sample_words(
            wordlists=wordlists,
            position_in_word=position_in_word,
            min_sequence_size=len(word_parts),
        )
        out.writelines(words)


def _generate_sample_words(
    wordlists: List[str],
    position_in_word: str,
    min_sequence_size: int,
    how_many: int = 50,
    template: str = "adverb verb adjective noun",
) -> List[str]:
    """Generate sample words to give the user an idea of what to expect"""
    # Read all the words
    words = dict()
    for wordlist in wordlists:
        word_part = Path(wordlist).stem
        with open(wordlist, "r") as file:
            words[word_part] = file.readlines()

    # Initialize the encoder with the designated template
    ordered = [words[part] for part in template.split(" ")]
    encoder = WordEncoder(word_lists=ordered, min_sequence_size=min_sequence_size)

    # Generate words
    word_size = f"[{MIN_LENGTH}, {MAX_LENGTH}]"
    print(
        f"Generating sample words for '{position_in_word}', {min_sequence_size} words, word size {word_size}..."
    )

    # Determine the minimum value represented by the desired word size (i.e., W*W)
    sizes = [len(o) for o in ordered[-min_sequence_size + 1 :]]
    min_for_desired_word_size = reduce(lambda x, y: x * y, sizes)

    # Determine the maximum value represented by the desired word size (i.e., W*W*W - 1)
    sizes = [len(o) for o in ordered[-min_sequence_size:]]
    max_for_desired_word_size = reduce(lambda x, y: x * y, sizes) - 1

    results: List[str] = list()
    for _ in range(0, how_many):
        val = random.randint(min_for_desired_word_size, max_for_desired_word_size)
        chosen = " ".join(encoder.encode(val))
        results.append(f"- {chosen}\n")

    return results


if __name__ == "__main__":
    main()
