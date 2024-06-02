import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from encoder.encoder import WordEncoder, EncoderException


class TestDecode(unittest.TestCase):
    def setUp(self):
        # Define word lists
        adverbs = ["absurdly", "busily", "capably"]
        verbs = ["abandoned", "bearded", "checked"]
        adjectives = ["able", "blond", "chubby"]
        nouns = ["apple", "bird", "cat", "dog"]
        self.words = [adverbs, verbs, adjectives, nouns]

    def test_should_fail(self):
        encoder = WordEncoder(self.words, 1)
        with self.assertRaises(EncoderException):
            more_than_available = encoder.get_max() + 1
            encoder.encode(more_than_available)

    def test_expected_results(self):
        test_cases = [
            (23, 1, "bearded chubby dog"),
            (24, 1, "checked able apple"),
            (107, 1, "capably checked chubby dog"),
            (12, 1, "bearded able apple"),
            (4, 1, "blond apple"),
        ]

        for expected, min_seq, words in test_cases:
            got = WordEncoder(self.words, min_seq).decode(words.split(" "))
            msg = f"Error {words:30} (min_words={min_seq:1}); expected: '{expected:3}', got: '{got:3}'"
            self.assertEqual(got, expected, msg=msg)

    def test_can_encode_and_decode_all_values(self):
        solution_space = range(0, WordEncoder(self.words, 1).get_max())
        test_cases = (
            [(i, 1) for i in solution_space]
            + [(i, 2) for i in solution_space]
            + [(i, 3) for i in solution_space]
            + [(i, 4) for i in solution_space]
        )

        for expected, min_words in test_cases:
            encoder = WordEncoder(self.words, min_words)
            encoded = encoder.encode(expected)
            encoded_str = " ".join(encoded)
            self.assertIsNotNone(encoded)

            got = encoder.decode(encoded)

            msg = f"Encoded '{expected:3}' (min_words={min_words:1}), got: '{encoded_str:30}', then decoded back to '{got:3}'"
            self.assertEqual(got, expected, msg)


if __name__ == "__main__":
    unittest.main()
