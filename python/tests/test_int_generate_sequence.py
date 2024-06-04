from datetime import datetime, timezone
import os
import sys
import unittest

from encoder.encoder import WordEncoder, load_wordlist
from encoder.generator import Generator, Resolution

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
            resolution=Resolution.MILLISECOND,
        )

        # Read words
        words = load_wordlist("resources/012_a4b591d", package_name="encoder.encoder")

        # Configure the encoder
        encoder = WordEncoder(words, 4)

        # ACT
        id = generator.next_id()
        sequence = encoder.encode(id)

        # ASSERT
        self.assertEqual(len(sequence), 4)

        got = encoder.decode(sequence)
        self.assertEqual(got, id)


if __name__ == "__main__":
    unittest.main()
