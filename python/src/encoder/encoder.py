"""
Encoder
=======

Contains the WordEncoder class that can encode integers to [word sequences]
and decode [word sequences] to integers.

Classes:
    EncoderException - Raised when a WordEncoder is misconfigured.
    WordEncoder - Encodes and decodes integers and [word sequences].
"""

from typing import List, Optional


class EncoderException(Exception):
    """
    Raised when a WordEncoder is misconfigured.
    """

    pass


class WordEncoder:
    """
    Encodes integers to [word sequences] and decodes [word sequences] to integers.

    Attributes:
        word_lists (List[List[str]]): Word lists used to map integers to words.
        min_sequence_size (int): What is the minimum sequence that should be returned.
                                 If not provided, it will default to the number
                                 word lists provided.
    """

    def __init__(
        self, word_lists: List[List[str]], min_sequence_size: Optional[int] = None
    ):
        """
        Constructs a new instance of WordEncoder.

        Parameters:
            word_lists (List[List[str]]): Word lists used to map integers to words.
            min_sequence_size (int): What is the minimum sequence that should be returned.
                                    If not provided, it will default to the number
                                    word lists provided.
        """
        self._word_lists = [[word.strip() for word in lst] for lst in word_lists]
        self._max_sequence = len(word_lists)

        # If the min_sequence is not provided, default to the maximum available
        if min_sequence_size is None:
            min_sequence_size = self._max_sequence

        # Ensure min_sequence_size is valid
        if not (1 <= min_sequence_size <= self._max_sequence):
            raise EncoderException(
                f"min_sequence_size must be between 1 and {self._max_sequence}"
            )
        self._min_sequence = min_sequence_size

        self._radices = [len(lst) for lst in self._word_lists]
        self._max_values = self._compute_max_values()
        self._abs_max = self._max_values[-1]

    def encode(self, number: int) -> List[str]:
        """
        Encodes an integer to a [word sequence].

        Parameters:
            number (int): The integer to encode.

        Returns:
            List[str]: The corresponding word sequence.
        """

        # Validate the input
        if number >= self._abs_max:
            raise EncoderException(
                f"The number ({number}) is too large to be encoded with up to {self._max_sequence} words (max: {self._max_values[-1] - 1})"
            )

        # Determine the number of words needed
        words_needed = self._determine_sequence_size(number)

        # Initialize indexes with -1, to protect against bugs (zeroes would be valid values and could not be distinguished)
        indexes = [-1] * self._max_sequence
        boundary = self._max_sequence - 1

        # Calculate the corresponding indexes for each word
        for i in range(boundary, boundary - words_needed, -1):
            # Populate the appropriate index, right-to-left
            list_size = self._radices[i]
            indexes[i] = number % list_size

            # Calculate the remaining value to be encoded by the next radix
            number //= list_size

        # Calculate the resulting word sequence
        input = list(zip(self._word_lists[-words_needed:], indexes[-words_needed:]))
        sequence = [lst[i] for lst, i in input]
        return sequence

    def decode(self, words: List[str]) -> int:
        """
        Decodes a [word sequence] to an integer.

        Parameters:
            List[str]: The word sequence to decode.

        Returns:
            int: The corresponding integer.
        """

        seq_length = len(words)
        if seq_length > self._max_sequence:
            raise EncoderException(
                f"The sequence contains more words that can be decoded with up to {self._max_sequence} words"
            )

        # Calculate the indices of each specified word
        relevant_words = self._word_lists[-seq_length:]
        indices = [relevant_words[idx].index(word) for idx, word in enumerate(words)]

        # Transform indexes into integers
        result = 0
        relevant_radices = self._radices[-seq_length:]
        for i, index in enumerate(indices):
            list_size = relevant_radices[i]
            result = result * list_size + index

        return result

    def get_max(self) -> int:
        """
        Returns the absolute max number that can be encoded by this class.

        Returns:
            int: An integer value that is the upper bound of integers that can be represented with the configured word lists.
        """
        return self._abs_max

    def _compute_max_values(self) -> List[int]:
        # Compute the maximum encodable values
        # The resulting indices are reversed compared to the list of words (first element represents last word)
        max_values = [1] * (self._max_sequence + 1)
        for i in range(1, (self._max_sequence + 1)):
            # With each added word we can represent (W) x (W-1) integers
            max_values[i] = max_values[i - 1] * self._radices[self._max_sequence - i]
        return max_values

    def _determine_sequence_size(self, number: int) -> int:
        # Determine the number of words needed to encode the result
        words_needed = self._min_sequence
        boundary = self._max_sequence + 1
        for i in range(self._min_sequence, boundary):
            words_needed = i
            if self._max_values[i] > number:
                break
        return words_needed
