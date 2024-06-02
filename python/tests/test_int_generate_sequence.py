from datetime import datetime, timezone
import os
import sys
from typing import List
import unittest

import pkg_resources

from encoder.encoder import WordEncoder
from encoder.generator import Generator

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


class TestIntegrationGenerateSequence(unittest.TestCase):
    def test_can_generate(self):
        # ARRANGE
        epoch = datetime(2024, 5, 30, tzinfo=timezone.utc).timestamp()

        # Configure the generator
        generator = Generator(
            epoch=epoch,
            machine_ids=[0],
            machine_id_bits=0,
            sequence_bits=0,
            resolution=0.001,  # millis
        )

        # Read words
        word_list = "resources/012_a4b591d"
        words = [
            read_from_resource(f"{word_list}/{word}.txt")
            for word in ["adverb", "verb", "adjective", "noun"]
        ]

        # Configure the encoder
        encoder = WordEncoder(words, 4)

        # ACT
        id = generator.next_id()
        sequence = encoder.encode(id)

        # ASSERT
        self.assertEqual(len(sequence), 4)

        got = encoder.decode(sequence)
        self.assertEqual(got, id)


def read_from_resource(name: str) -> List[str]:
    """Reads data from a resource file within a package, split by lines."""
    data_path = pkg_resources.resource_filename("encoder.encoder", name)
    with open(data_path, "r") as file:
        data = file.readlines()
    return data


if __name__ == "__main__":
    unittest.main()
