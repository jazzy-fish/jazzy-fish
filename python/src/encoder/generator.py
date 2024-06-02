"""
Generator
=========

Contains the Generator and ThreadSafeGenerator classes which can generate unique integer identifiers
that respect the configured settings and can be later converted to [word sequences] with a WordEncoder.

Classes:
    Generator - Generates unique integer identifiers with configurable properties.
    GeneratorException - Raised when a Generator is misconfigured.
    ThreadSafeGenerator - Wraps the Generator class, making it thread safe (wrapping `next_id()` with a lock).
"""

from collections import defaultdict
import threading
import time
from typing import Callable, Dict, List


class Generator:
    """
    Generates unique integer identifiers with configurable properties.

    Attributes:
        epoch (float): The epoch that the time component will be relative to; set to 0.0 for UNIX time.
        resolution (float): The time unit resolution, to which the other parameters will be tied to.
                            For example, if configured to 1, IDs will be generated relative to seconds,
                            and if configured to 0.001, IDs will be relative to milliseconds.
        machine_ids (List[int]): A list of machine identifiers owned by the current instance;
                                 at least one value must be provided; duplicates will be ignored.
        machine_id_bits (int): How many bits are allocated for the machine ID;
                               only positive integers are valid.
        sequence_bits (int): How many bits are allocated for the local sequence;
                             only positive integers are valid.
                             If set to 0, only one identifier can be generated per machine in each time unit
    """

    def __init__(
        self,
        epoch: float,
        resolution: float,
        machine_ids: List[int],
        machine_id_bits: int,
        sequence_bits: int,
    ):
        """
        Constructs a new instance of Generator.

        Parameters:
            epoch (float): The epoch that the time component will be relative to; set to 0.0 for UNIX time.
            resolution (float): The time unit resolution, to which the other parameters will be tied to.
                                For example, if configured to 1, IDs will be generated relative to seconds,
                                and if configured to 0.001, IDs will be relative to milliseconds.
            machine_ids (List[int]): A list of machine identifiers owned by the current instance;
                                    at least one value must be provided; duplicates will be ignored.
            machine_id_bits (int): How many bits are allocated for the machine ID;
                                only positive integers are valid.
            sequence_bits (int): How many bits are allocated for the local sequence;
                                only positive integers are valid.
                                If set to 0, only one identifier can be generated per machine in each time unit
        """

        self.epoch = epoch
        # Allows replacing the time in tests
        self.current_time: Callable[[], float] = lambda: time.time()
        self.resolution = resolution

        self.machine_id_bits = machine_id_bits
        max_machine_id = (1 << machine_id_bits) - 1 if machine_id_bits > 0 else 0

        # Validates the specified machine IDs
        if not machine_ids:
            raise GeneratorException("At least one machine ID must be provided")

        self.machine_ids = list(set(machine_ids))
        for mid in self.machine_ids:
            if not 0 <= mid <= max_machine_id:
                raise GeneratorException(
                    f"Specified machine ID {mid} is invalid for the configured maximum bit size: {machine_id_bits}"
                )

        self.sequence_bits = sequence_bits
        self.max_sequence = (1 << sequence_bits) - 1 if sequence_bits > 0 else 0

        # Variables that help handle multiple machine IDs and corresponding sequences
        self.sequences: Dict[int, int] = defaultdict(int)
        self.last_times: Dict[int, int] = defaultdict(lambda: -1)
        self.current_machine_index = 0

    def next_id(self) -> int:
        """
        Generates unique values according to the configured class settings.
        If the maximum sequences per time unit have already been generated,
        the method will busy-wait until the next time unit has been reached.

        Returns:
            int: A unique integer identifier, relative to the configured time unit, and machine ID.
        """

        machine_id = self._next_machine_id()
        sequence = self.sequences[machine_id]

        current_time = self._current_time()
        last_time = self.last_times[machine_id]

        if current_time < last_time:
            # Delayed thread, allow it to catch-up
            current_time = self._wait_for_next_time(current_time, last_time)

        if current_time == last_time:
            # TODO: might need to check self.sequence_bits > 0
            sequence += 1
            if sequence > self.max_sequence:
                current_time = self._wait_for_next_time(current_time, last_time)
                sequence = 0
                last_time = current_time
        else:
            sequence = 0
            last_time = current_time

        self.last_times[machine_id] = last_time
        self.sequences[machine_id] = sequence

        id = current_time << (self.machine_id_bits + self.sequence_bits)
        if self.machine_id_bits > 0:
            id |= machine_id << self.sequence_bits
        if self.sequence_bits > 0:
            id |= sequence

        return id

    def _current_time(self) -> int:
        return int((self.current_time() - self.epoch) / self.resolution)

    def _wait_for_next_time(self, current_time: int, last_time: int) -> int:
        # busy wait until the required time-unit passes
        while current_time <= last_time:
            current_time = self._current_time()
        return current_time

    def _next_machine_id(self) -> int:
        machine_id = self.machine_ids[self.current_machine_index]
        self.current_machine_index = (self.current_machine_index + 1) % len(
            self.machine_ids
        )
        return machine_id


class ThreadSafeGenerator(Generator):
    """
    Wraps the Generator class, making it thread safe (wrapping `next_id()` with a lock).

    Attributes:
       epoch (float): The epoch that the time component will be relative to; set to 0.0 for UNIX time.
       resolution (float): The time unit resolution, to which the other parameters will be tied to.
                           For example, if configured to 1, IDs will be generated relative to seconds,
                           and if configured to 0.001, IDs will be relative to milliseconds.
       machine_ids (List[int]): A list of machine identifiers owned by the current instance;
                                at least one value must be provided; duplicates will be ignored.
       machine_id_bits (int): How many bits are allocated for the machine ID;
                              only positive integers are valid.
       sequence_bits (int): How many bits are allocated for the local sequence;
                            only positive integers are valid.
                            If set to 0, only one identifier can be generated per machine in each time unit
    """

    def __init__(
        self,
        epoch: float,
        resolution: float,
        machine_ids: List[int],
        machine_id_bits: int,
        sequence_bits: int,
    ):
        """
        Constructs a ThreadSafeGenerator.

        Parameters:
            epoch (float): The epoch that the time component will be relative to; set to 0.0 for UNIX time.
            resolution (float): The time unit resolution, to which the other parameters will be tied to.
                                For example, if configured to 1, IDs will be generated relative to seconds,
                                and if configured to 0.001, IDs will be relative to milliseconds.
            machine_ids (List[int]): A list of machine identifiers owned by the current instance;
                                    at least one value must be provided; duplicates will be ignored.
            machine_id_bits (int): How many bits are allocated for the machine ID;
                                only positive integers are valid.
            sequence_bits (int): How many bits are allocated for the local sequence;
                                only positive integers are valid.
                                If set to 0, only one identifier can be generated per machine in each time unit
        """
        super().__init__(epoch, resolution, machine_ids, machine_id_bits, sequence_bits)
        self.lock = threading.Lock()

    def next_id(self) -> int:
        """
        Generates unique values in a thread safe manner, by wrapping Generator.next_id() with a lock.

        Returns:
            int: A unique integer identifier, relative to the configured time unit, and machine ID.
        """

        with self.lock:
            return super().next_id()


class GeneratorException(Exception):
    """
    Raised when a Generator is misconfigured.
    """

    pass
