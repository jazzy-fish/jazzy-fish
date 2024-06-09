from datetime import datetime, timezone
from jazzy_fish.encoder import WordEncoder, Wordlist
from jazzy_fish.generator import Generator, Resolution


def main() -> None:
    """Functional test that ensures the library can be imported and utilized"""

    epoch = datetime(2024, 5, 30, tzinfo=timezone.utc).timestamp()

    generator = Generator(
        epoch=epoch,
        machine_ids=[0],
        machine_id_bits=0,
        sequence_bits=0,
        resolution=Resolution.MILLISECOND,
    )
    wordlist = Wordlist.load("resources/012_8562fb9", "jazzy_fish.encoder")
    encoder = WordEncoder(wordlist, min_phrase_size=4)

    id = generator.next_id()
    encoded = encoder.encode(id)

    if not (encoded.key_phrase):
        raise RuntimeError(
            f"Expected valid encoded keyphrase, got {encoded.key_phrase}"
        )

    if len(encoded.key_phrase) != 4:
        raise RuntimeError(f"Expected 4 words, got {len(encoded.key_phrase)}")

    if not (encoded.abbr):
        raise RuntimeError(f"Expected valid abbreviation, got {encoded.abbr}")

    got = encoder.decode(encoded.key_phrase)
    if not (encoded.abbr):
        raise RuntimeError(f"Expected to correctly decode value ({id}), got {got}")

    print("OK.")


if __name__ == "__main__":
    main()
