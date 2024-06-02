import os
import sys
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from preprocessor.helpers import least_similar_words


class TestSelect(unittest.TestCase):
    def test_deterministic_shuffle(self):
        words = ["abaccus", "abba", "dumb", "dumbell", "zorro", "zutanix"]
        expected = ["abaccus", "zutanix", "dumb", "abba", "dumbell", "zorro"]
        result = least_similar_words(words, 6)
        self.assertEqual(result, expected)

    def test_shuffled_limit(self):
        words = ["abaccus", "abba", "dumb", "dumbell", "zorro", "zutanix"]
        expected = ["abaccus", "zutanix"]
        result = least_similar_words(words, 2)
        self.assertEqual(result, expected)

    def test_odd_word_list(self):
        words = ["abaccus", "abba", "dumb"]
        expected = ["abaccus", "dumb"]
        result = least_similar_words(words, 2)
        self.assertEqual(result, expected)

    def test_impossible_shuffle(self):
        words = ["zutanix", "dumbell"]
        expected = ["dumbell", "zutanix"]
        result = least_similar_words(words, 2)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
