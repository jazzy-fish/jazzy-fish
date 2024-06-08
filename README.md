# Jazzy Fish - Sufficiently-large, unique, human-friendly identifiers

![Build Status](https://github.com/jazzy-fish/jazzy-fish/actions/workflows/python-tests.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/jazzy-fish.svg)](https://badge.fury.io/py/jazzy-fish)
[![Python Versions](https://img.shields.io/pypi/pyversions/jazzy-fish.svg)](https://pypi.org/project/jazzy-fish/)
[![License](https://img.shields.io/github/license/jazzy-fish/jazzy-fish.svg)](LICENSE)

Jazzy Fish is a library that helps you generate a sufficient number of identifiers, with a human-friendly kick.

This is not a new idea and similar implementation can be seen in various places (i.e., GitHub new repository name [suggestions](https://github.com/new).

Jazzy Fish is able to generate word sequences that can be mapped to unique integer values, which can be used as identifiers.

The implementation roughly works as follows:

- configure a `Generator`, more information below
- call `generator.next_id()`, which returns a unique integer
- call `Encoder.encode(id)`, which returns a `[word sequence]`
- optionally, if a word sequence needs to be decoded into an integer, call `Encoder.decode([word sequence])`

## Terminology

- `word part`: parts of speech used in the English language that can be used to form sentences/phrases: adverbs, verbs, adjectives, and nouns
- `dictionary`: a list of English words categorized by _word part_, which is used to generate _wordlists_
- `wordlist`: a list of *word part*s that can be combined to generate a large number of *key phrase*s
- `key phrase`: a uniquely ordered sequence of words, each of a certain _word part_, which can be mapped to a unique integer identifier
- `identifier`: a numerical (integer) value that can be used to represent unique entities
- `word prefixes`: TBD, rename

## Configuring a Generator

Integer IDs are constructed by combining 3 parts:

- a `timestamp`: can be relative to the UNIX epoch, or a custom epoch - to maximize the possible solution size;
  the timestamp can be chosen between seconds and milliseconds, in increments of 1/10ms (1s, 1/10s, 1/100s, 1ms)
- a `machine id`: since it may be necessary to run multiple generators (i.e., in distributed systems), the solution domain can be partitioned by multiple 'machines'
- a `sequence id`: representing a number of identifiers that can be generated, all things being equal (e.g., same time, same machine)

Thus, the algorithm is configurable enough to split a solution domain (e.g., N potential word combinations, where N is a large integer) into smaller partitions, that can be reasoned about in terms of: `For how many years can IDs/word sequences be generated before the implementation needs to be changed?`

The idea behind this implementation is also inspired from Bitcoin's Improvement Proposal [39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki).

Note: The BIP39 implementation uses a single word list to convert 12 or 24 unique words out of a total of 2048 words into a very large integer that can be used to derive secret keys.

Jazzy Fish different from BIP39 in that it uses multiple word lists (specifically, adverbs, verbs, adjectives, and nouns) to generate word sequences that are similar to natural (English) language, with the assumption that sequences such as `yellow cat`, `hectic fish`, `dreadful elephant` (while somewhat nonsensical) are easy to memorize by humans used to combining word parts. So, the aim of this library is to choose sufficiently-large word lists that can generate sufficiently-large unique word sequences, for a reasonable duration (i.e., several years or more).

Another relevant detail of this algorithm, is its ability to map chosen word sequences to smaller prefixes that can be used to form constant-length identifiers.
While each sequence maps to an integer, remembering integers is hard for most humans. Thus, based on this implementation's assumption that humans can remember structured sentences, it selects the input wordlists in such a way that, for a given and pre-configured prefix length, there exists a single word that corresponds to that prefix.

For example, given a prefix length of size=1, `yellow cat` can be encoded to `yc` and then decoded back to the same two words. In this example, `yellow` is an adjective, and `cat` is a noun. There do not exist any other adjectives that start with `y`, nor nouns that start with `c` in our input word lists.

The reference implementation of the algorithm comes with a default wordlist of prefix 3, containing adverbs, verbs, adjectives, and nouns.

It can map the following solution domains:

- 2,178,560 unique combinations of `adjective noun`
- 2,740,628,480 unique combinations of `verb adjective noun`
- 1,205,876,531,200 unique combinations of `adverb verb adjective noun`

Two-word sequences may be impractical for sustained identifier generation, however, three word and four word sequences can sustain 87 and 38,238 years respectively at a rate of 1 identifier generated per second, using a single machine.

However, the default implementation can be changed to using longer prefixes and you can also bring your own wordlists, if desired.

The [preprocessor](python/src/preprocessor) package contains code that can process input wordlists and generate input word list combinations,
which can be inspected to help users infer the best choice depending on use-case.

## Contents

This directory contains the following resources:

- [python](./python): Python implementation of the Jazzy Fish ID generator
- [wordlists](./wordlists): Several input wordlist versions that extensively cover the English language (for provenance, see below)
  the default wordlist was generated using words from [wordlist 5](./wordlists/5).

### Wordlist origin

The included input wordlists were compiled from various free sources, which can be found at the following URLs:

- <http://www.ashley-bovan.co.uk/words/partsofspeech.html>
- <https://github.com/dwyl/english-words>
- <https://gist.github.com/hugsy/8910dc78d208e40de42deb29e62df913>
- <https://github.com/verachell/English-word-lists-parts-of-speech-approximate>
- <https://people.sc.fsu.edu/~jburkardt/datasets/words/words.html>
- <https://people.sc.fsu.edu/~jburkardt/datasets/words/wordlist.txt>
- <https://github.com/touchtypie/english-words>
- <https://huggingface.co/datasets/Maximax67/English-Valid-Words>
- <https://www.desiquintans.com/nounlist>
- <https://people.sc.fsu.edu/~jburkardt/datasets/words/anagram_dictionary.txt>

Great care was taken to exclude offensive words (and an exclude list can be found in the [python/src/preprocessor](./python/src/preprocessor) package).
However, as humans have varied cultures and cultural differences, these lists may still contain such words.
If you spot any such words, please **open an issue in this repository**, flagging the relevant word.
The code and provided wordlists are provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, as detailed
in the Apache 2.0 license. **Please take great care to vet the code and wordlists before using it in a production setting!**
You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with
Your exercise of permissions under this License.

## Quickstart

### Python

You can install the library directly from git:
`pip install git+https://github.com/jazzy-fish/jazzy-fish#subdirectory=python`

## Developers

This repository uses `pre-commit` to manage git hooks. It is installed by default in the python library, and you can also
install it manually with `pip install pre-commit`.

After cloning the repo with `git clone git@github.com:jazzy-fish/jazzy-fish.git` you should install git hooks with:

```shell
pre-commit install
```

You can manually run the hooks against all files with `pre-commit run --all-files` or
read the documentation at <https://pre-commit.com/>.

## Choosing a word list

The values below are computed based on the [wordlists/5](./wordlists/5) dictionary, which aims to include
words more commonly used in the English language. You should verify that the resulting wordlist contains
appropriate values for your use-case.

You can generate these by running the [preprocessor.generate_words](python/src/preprocessor/generate_words.py) script.

### Second-frequency

For a more seldom generation frequency, use one of the following wordlists:

```text
[        46 years at 1/s ] [      1,457,033,600] ('adverb', 'verb', 'adjective', 'noun' ) for prefix: '01    ' [SEQ] - 8-byte ID, sequential abbreviation
[        87 years at 1/s ] [      2,740,628,480] ('verb', 'adjective', 'noun'           ) for prefix: '012   ' [SEQ] - 9-byte ID, sequential abbreviation
[       400 years at 1/s ] [     12,615,189,300] ('verb', 'adjective', 'noun'           ) for prefix: '024   ' [RND] - largest 9 byte ID
[       852 years at 1/s ] [     26,862,324,450] ('verb', 'adjective', 'noun'           ) for prefix: '1234  ' [RND] - 12-byte ID
[       869 years at 1/s ] [     27,399,835,008] ('adverb', 'verb', 'adjective', 'noun' ) for prefix: '02    ' [RND] - largest 8-byte ID
[    38,238 years at 1/s ] [  1,205,876,531,200] ('adverb', 'verb', 'adjective', 'noun' ) for prefix: '012   ' [SEQ] - 12-byte ID, sequential abbreviation
[   197,212 years at 1/s ] [  6,219,288,324,900] ('adverb', 'verb', 'adjective', 'noun' ) for prefix: '024   ' [RND] - largest 12-byte ID
[   543,674 years at 1/s ] [ 17,145,317,425,600] ('adverb', 'adjective', 'verb', 'noun' ) for prefix: '0123  ' [SEQ] - 16-byte ID, sequential abbreviation
[ 1,098,369 years at 1/s ] [ 34,638,169,276,128] ('adverb', 'verb', 'adjective', 'noun' ) for prefix: '01234 ' [SEQ] - 20-byte ID, sequential abbreviation
```

### Millisecond-frequency

If you require a volume of identifiers that can sustain millisecond-frequency generation,
use one of the following wordlists:

```text
[   197 years at 1/ms] [     6,219,288,324,900] ('adverb', 'verb', 'adjective', 'noun'     ) for prefix: '024   ' [RND] - largest 12-byte ID
[   544 years at 1/ms] [    17,145,317,425,600] ('adverb', 'adjective', 'verb', 'noun'     ) for prefix: '0123  ' [SEQ] - 16-byte ID, sequential abbreviation
[   762 years at 1/ms] [    24,016,903,475,712] ('adverb', 'verb', 'adjective', 'noun'     ) for prefix: '0234  ' [RND] - largest 16-byte ID
[ 1,098 years at 1/ms] [    34,638,169,276,128] ('adverb', 'verb', 'adjective', 'noun'     ) for prefix: '01234 ' [SEQ] - largest 20-byte ID, sequential abbreviation
```
