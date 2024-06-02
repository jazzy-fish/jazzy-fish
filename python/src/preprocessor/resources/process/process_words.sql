CREATE
OR REPLACE TABLE words_by_prefix AS
WITH RECURSIVE
    -- Recursively generate all prefixes larger than one character, for each word in the list
    prefixes AS (
        SELECT
            prefix_length,
            position,
            identifier,
            word_part,
            word,
            word AS prefix
        FROM
            words
        UNION ALL
        -- Recurse into the table, one less character at a time
        SELECT
            prefix_length,
            position,
            identifier,
            word_part,
            word,
            SUBSTRING(prefix, 1, LENGTH (prefix) - 1) AS prefix
        FROM
            prefixes
        WHERE
            LENGTH (prefix) > 1
    ),
    -- Exclude words that prefix selected words to avoid including very similar words (e.g., abac and abacus)
    unique_words AS (
        SELECT DISTINCT
            prefix_length,
            position,
            identifier,
            word_part,
            word
        FROM
            words
        WHERE
            -- the word should not be a prefix for another word
            word NOT IN (
                SELECT
                    prefix
                FROM
                    prefixes
                WHERE
                    prefix != word
            )
        ORDER BY
            prefix_length,
            position,
            identifier,
            word_part,
            word
    ),
    -- group words by their prefix, creating a list of suitable words per prefix
    agg_by_prefix AS (
        SELECT
            position,
            word_part,
            identifier,
            prefix_length,
            STRING_SPLIT (
                STRING_AGG (
                    word,
                    ','
                    ORDER BY
                        word
                ),
                ','
            ) AS words
        FROM
            unique_words
        GROUP BY ALL
    ),
    -- store all relevant fields
    full_list AS (
        SELECT
            position,
            word_part,
            identifier,
            prefix_length,
            words AS all_words,
            LENGTH (all_words) AS available_words,
            CAST(
                LEAST (LENGTH (all_words), POWER(2, prefix_length)) AS INTEGER
            ) AS max_words_for_prefix,
            LIST_SORT (LIST_SLICE (words, 1, POWER(2, prefix_length))) AS first_words
        FROM
            agg_by_prefix
    ),
    -- and call an UDF to select words that have a lower chance of being similar to each other
    final AS (
        SELECT
            full_list.*,
            least_similar_words (all_words, max_words_for_prefix) AS selected_words
        FROM
            full_list
    )
SELECT
    *
FROM
    final;
