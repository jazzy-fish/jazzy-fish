#!/bin/bash
# Output the currently chosen wordlist

PYTHONPATH=python/src python <<END | tee -a ../docs/comparison.txt
from preprocessor.helpers import MIN_LENGTH, MAX_LENGTH
word_size = f"[{MIN_LENGTH}, {MAX_LENGTH}]"
print(f"\n\n# Stats for word length {word_size}...\n")
END
