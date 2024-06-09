"""
Jazzy Fish
==========

This package contains the code required by clients who wish to generate jazzy-fish keyphrases.

Modules:
    encoder - Contains the WordEncoder class that can encode integers to [word sequences]
              and decode [word sequences] to integers.
    generator - Contains the Generator and ThreadSafeGenerator classes which can generate unique integer identifiers
                that respect the configured settings and can be later converted to [word sequences] with a WordEncoder.

Usage:

    Import the package and use the provided classes:

    from datetime import datetime, timezone
    from jazzy_fish.encoder import WordEncoder, load_wordlist
    from jazzy_fish.generator import Generator, Resolution

    # Configure a starting epoch for the sequence
    # Alternatively, you can use the UNIX epoch (0), but that will exhaust some of the solution space
    epoch = datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp()

    # Configure the generator
    generator = Generator(
        epoch=epoch,        # Define the epoch
        machine_ids=[0],    # Configure the machine id (partition)
        machine_id_bits=0,  # A single machine
        sequence_bits=0,    # Allow a single ID per machine per time unit
        resolution=Resolution.MILLISECOND,  # Results in one ID per ms.
    )

    # Load the default word list included in the jazzy-fish library
    words = load_wordlist("resources/012_8562fb9", package_name="jazzy_fish.encoder")
    # and initialize an encoder
    encoder = WordEncoder(words, 4)

    # Generate an ID and encoded it to a word sequence
    id = generator.next_id()
    sequence = encoder.encode(id)

"""

from .encoder import KeyPhrase, WordEncoder, Wordlist
from .generator import Generator, Resolution, ThreadSafeGenerator

__all__ = [
    "Generator",
    "KeyPhrase",
    "Resolution",
    "ThreadSafeGenerator",
    "WordEncoder",
    "Wordlist",
]