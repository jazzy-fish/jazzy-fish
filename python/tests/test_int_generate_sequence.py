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
        words = load_wordlist("resources/012_d188dfc", package_name="encoder.encoder")

        # Configure the encoder
        encoder = WordEncoder(words, id_char_positions=[0, 1, 2], min_sequence_size=4)

        # ACT
        id = generator.next_id()
        encoded = encoder.encode(id)

        # ASSERT
        self.assertEqual(len(encoded.key_phrase), 4)

        got = encoder.decode(encoded.key_phrase)
        self.assertEqual(got, id)


if __name__ == "__main__":
    unittest.main()
