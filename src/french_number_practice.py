#!/usr/bin/env python3

from __future__ import annotations
from collections import deque

import functools
import logging
import random
import sys
import time
import argparse

import num2words


class Config:
    def __init__(self) -> None:
        pass


class FrenchNumberPracticeConfig(Config):
    def __init__(self) -> None:
        super().__init__()
        self.MIN_NUMBER = 0
        self.MAX_NUMBER = 100
        self.LANGUAGE = "fr"

    def __repr__(self) -> str:
        repr_text = (
            f"{self.MIN_NUMBER=}",
            f"{self.MAX_NUMBER=}",
            f"{self.LANGUAGE=}",
        )
        return f"{self.__class__.__name__}{repr_text}"


class Interval:
    def __init__(self, start: int, end: int) -> None:
        if end < start:
            raise ValueError("Start must be less than or equal to end")
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        repr_text = (
            f"{self.start=}",
            f"{self.end=}",
        )
        return f"{__class__.__name__}{repr_text}"

    def limit_bottom(self, x: int) -> Interval:
        """
        limit the start value to x.
           ~~~~~~
             /
            /
        ___/
           ^------ x
        """
        self.start = max(self.start, x)
        return self

    def limit_top(self, x: int) -> Interval:
        """
        Limit the end value to x.
              ___
             /^------ x
            /
           /
        ~~~~~~
        """
        self.end = min(self.end, x)
        return self


class HalfOpenedInterval(Interval):
    def __init__(self, start: int, end: int) -> None:
        super().__init__(start, end)

    def to_opened_interval(self):
        """
        Returns range() function friendly interval. For instance it
        treats [s, t) as if it were [s, t].
        """
        return HalfOpenedInterval(self.start, self.end + 1)

    def is_in_range(self, x: int) -> bool:
        """
        Check if an argument x is in the range.

        Args:
            x (int): a value to be checked.

        Returns:
            bool: True on x is in the range, return False is it isn't.
        """
        return self.start <= x < self.end

    def is_in_range_as_opened(self, x: int) -> bool:
        return self.start <= x <= self.end


def try_int_conversion(test_string: str) -> None:
    """
    Tries integer conversion from test_string.

    Args:
        test_string (str): a string to be tested.

    Raises:
        ValueError: the given string is no longer number.
    """
    try:
        int(test_string)
    except ValueError:
        raise ValueError("Please enter a number")


def test_in_range_on_preparation(coordinates: Interval, config: FrenchNumberPracticeConfig) -> None:
    if (
        config.MIN_NUMBER <= coordinates.start <= config.MAX_NUMBER and
        config.MIN_NUMBER <= coordinates.end <= config.MAX_NUMBER
    ):
        return
    raise ValueError("Both start and end must be within a value from {0:d} to {1:d}".format(
        config.MIN_NUMBER,
        config.MAX_NUMBER
    ))


class TimerResult:
    """
    A dedicated class to store / show the time taken
    """

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.express()}")'

    def express(self) -> str:
        minutes, remainder = divmod(self.seconds, 60)
        seconds = round(remainder, 3)
        return "{:02d}:{:06.3f}".format(int(minutes), seconds)


class Timer:
    """
    A dedicated class to measure the time taken in execution of a function
    """

    def __init__(self) -> None:
        self.elapsed_seconds = 0.0
        self.started_seconds = 0.0

    def __repr__(self):
        self._current_elapsed()
        repr_text = (
            f"{self.elapsed_seconds=}",
            f"{self.started_seconds=}",
            f"{self.elapsed_seconds=}",
        )
        return f"{self.__class__.__name__}{repr_text}"

    def _current_elapsed(self) -> float:
        self.elapsed_seconds = time.time() - self.started_seconds
        return self.elapsed_seconds

    def start(self) -> Timer:
        self.started_seconds = time.time()
        return self

    def stop(self) -> Timer:
        self._current_elapsed()
        return self

    def execute(self, user_function) -> Timer:
        user_function()
        return self

    def retrieve_result(self) -> TimerResult:
        return TimerResult(self.elapsed_seconds)


class PlayingStatus:
    """
    A stateful class that holds the current status of the game.

    Args:
        queue: A set of the problems.
        timer (Timer): A timer that measures the time elapsed.
    """

    def __init__(self, queue, timer: Timer) -> None:
        self.attempts_count = 0
        self.correct_successive_count = 0
        self.correct_successive_count_max = 0
        self.mistakes_count = 0
        self.queue_length = len(queue)
        self.timer = timer

    def __repr__(self) -> str:
        repr_text = (
            f"{self.attempts_count=}",
            f"{self.correct_successive_count=}",
            f"{self.correct_successive_count_max=}",
            f"{self.mistakes_count=}",
            f"{self.queue_length=}",
            f"{self.timer=}",
        )
        return f"{__class__.__name__}{repr_text}"

    def __solved(self):
        self.attempts_count += 1
        self.correct_successive_count_max = max(
            self.correct_successive_count_max, self.correct_successive_count
        )

    def correct(self) -> None:
        """
        Process on correct answer
        """
        self.correct_successive_count += 1
        self.__solved()

    def wrong(self) -> None:
        """
        Process on wrong answer
        """
        self.correct_successive_count = 0
        self.mistakes_count += 1
        self.__solved()

    def freeze_with_finished_time(self, timer_result: TimerResult) -> PlayingStatusResult:
        return PlayingStatusResult(self, timer_result)


class PlayingStatusResult:

    def __init__(self, playing_status: PlayingStatus, timer_result: TimerResult) -> None:
        self.playing_status = playing_status
        self.timer_result = timer_result

    def __repr__(self) -> str:
        return f"{__class__.__name__}({self.playing_status}, {self.timer_result=})"

    def show_end_message(self) -> None:
        lines = [
            "{0:<50} {1} / {2}".format(
                "Total problems solved (actual / original)",
                self.playing_status.attempts_count - self.playing_status.mistakes_count,
                self.playing_status.queue_length
            ),
            "{0:<50} {1}".format(
                "Total mistakes made",
                self.playing_status.mistakes_count
            ),
            "{0:<50} {1}".format(
                "Maximum successive correct answer",
                self.playing_status.correct_successive_count_max
            ),
            "{0:<50} {1}".format(
                "Total time spent",
                self.timer_result.express()
            ),
        ]

        print("You solved all! Here's the summary:")
        for line in lines:
            print(f"  {line}")


class Validator:
    """
    A validator handler.
    """

    def __init__(self, user_functions) -> None:
        self.user_functions = user_functions


class InplayingFrenchValidator(Validator):
    """
    A set of validations/dependency to be used in playing games.

    Args:
        cooodinates (HalfOpenedInterval): Checks if the input value is with in this range.
        *user_functions: Callback function(s) to be executed inside the validation process.
    """

    def __init__(self, coordinates: HalfOpenedInterval, *user_functions) -> None:
        super().__init__(user_functions)
        self.coordinates = coordinates

    def is_valid(self, input_str: str) -> bool:
        try:
            for user_func in self.user_functions:
                user_func(test_string=input_str)
            if not self.coordinates.is_in_range_as_opened(int(input_str)):
                raise ValueError("The value must be within a value from {0:d} to {1:d}".format(
                    self.coordinates.start,
                    self.coordinates.end
                ))

        except ValueError as e:
            logger.error(e)
            return False
        return True


class ProblemBuilderFrenchValidator(Validator):
    """
    A set of validations needed to generate flawless problem sets.
    """

    def __init__(self, *user_functions) -> None:
        super().__init__(user_functions)

    def is_valid(self, coordinates: Interval) -> bool:
        try:
            for user_func in self.user_functions:
                user_func(coordinates=coordinates)
        except ValueError as e:
            logger.error(e)
            return False
        return True


class Card:

    def __init__(self, problem: str, answer: str) -> None:
        self.problem = problem
        self.answer = answer

    def __repr__(self) -> str:
        repr_text = (
            f"{self.problem}",
            f"{self.answer}"
        )
        return f"{__class__.__name__}{repr_text}"


class CardFrench(Card):
    """
    A class that represents a piece of flip card.

    Args:
        problem (str): A player sees this first, and then guesses the answer for this.
        answer (str): A player needs to answer this.
    """

    def __init__(self, problem: str, answer: str) -> None:
        super().__init__(problem, answer)


class ProblemBuilder:
    def __init__(self, config: Config) -> None:
        self.problem_set = []

    def get_queue(self) -> None:
        raise NotImplementedError("Subclasses should implement this!")


class ProblemBuilderFrench(ProblemBuilder):
    """
    Generates a pair of numbers represented in French and arabic numerals.

    Args:
        coordinates: Generates numbers (problems) within this range.
    """

    def __init__(self, coordinates: HalfOpenedInterval, config: FrenchNumberPracticeConfig) -> None:
        super().__init__(config)
        self.coordinates = coordinates
        self.config = config

    def get_queue(self) -> deque:
        """
        Get a queue of sets of problem, which is shuffled.
        """

        for n in range(self.coordinates.start, self.coordinates.end):
            self.problem_set.append(CardFrench(
                num2words.num2words(n, lang=self.config.LANGUAGE),
                str(n),
            ))

        random.shuffle(self.problem_set)
        return deque(self.problem_set)


class Engine:
    """
    A set of primary routines.
    """

    def __init__(self, queue: deque, playing_status: PlayingStatus, validator: InplayingFrenchValidator) -> None:
        self.queue = queue
        self.playing_status = playing_status
        self.validator = validator

    def enable_loop(self) -> None:
        while self.queue:
            card = self.queue.pop()
            is_solved = False

            assert (isinstance(card, CardFrench))

            while not is_solved:
                display = card.problem
                try:
                    guess = input(f"{display}: ")
                except (KeyboardInterrupt, EOFError) as e:
                    logger.error(e)
                    self.show_correct_answer(card.answer)
                    return

                if guess == "quit":
                    self.queue.appendleft(card)
                    self.show_correct_answer(card.answer)
                    break
                elif not self.validator.is_valid(guess):
                    continue
                elif guess != card.answer:
                    print("Guess again")
                    self.queue.appendleft(card)
                    self.playing_status.wrong()
                else:
                    self.say_compliment()
                    self.playing_status.correct()
                    is_solved = True

    def play_then_retrieve_result(self) -> PlayingStatusResult:
        timer_result = self.playing_status.timer.start(
        ).execute(
            self.enable_loop
        ).stop(
        ).retrieve_result()
        return self.playing_status.freeze_with_finished_time(timer_result)

    def say_compliment(self) -> None:
        logger.debug(self.playing_status)
        if self.playing_status.correct_successive_count < 1:
            print("Good guess!")
            return
        print("Good guess! (consecutive good answers: {0:<d})".format(
            self.playing_status.correct_successive_count
        ))

    def show_correct_answer(self, correct_answer: str) -> None:
        print(f"The answer: {correct_answer}")


class Game:
    """
    A collections of general methods and settings.
    """

    def __init__(self, config: FrenchNumberPracticeConfig) -> None:
        self.config = config
        logger.debug(config)

    def get_cordinates_input(self) -> HalfOpenedInterval:
        """
        Defines a range by a user input.
        """
        print("Specify the two values for the start and end of the "
              "range.")
        print("The values must be separated by a space:")

        validated = False
        coordinates_half_open = HalfOpenedInterval(-1, -1)

        while not validated:
            try:
                input_str = input("Input the range [from, to]: ")
            except (KeyboardInterrupt, EOFError) as e:
                logger.error(e)
                sys.exit(1)

            split_values = input_str.split()

            try:
                if not len(split_values) == 2:
                    raise ValueError(
                        "Two numbers must be entered, separated by a space."
                    )
                for try_string in split_values:
                    try_int_conversion(try_string)
            except ValueError as e:
                logger.error(e)
                continue

            start, end = [int(x) for x in split_values]

            try:
                coordinates_half_open = HalfOpenedInterval(start, end)
                validated = ProblemBuilderFrenchValidator(
                    functools.partial(
                        test_in_range_on_preparation,
                        config=self.config
                    ),
                ).is_valid(coordinates_half_open)
            except ValueError as e:
                logger.error(e)

        coordinates = coordinates_half_open.limit_bottom(
            self.config.MIN_NUMBER
        ).limit_top(
            self.config.MAX_NUMBER
        )

        return HalfOpenedInterval(coordinates.start, coordinates.end)

    def play(self) -> None:
        coordinates = self.get_cordinates_input()
        logger.debug(coordinates)

        queue = ProblemBuilderFrench(
            coordinates.to_opened_interval(),
            self.config
        ).get_queue()

        validator = InplayingFrenchValidator(
            coordinates,
            try_int_conversion,
        )

        p = Engine(
            queue,
            PlayingStatus(
                queue,
                Timer(),
            ),
            validator,
        )

        play_result = p.play_then_retrieve_result()
        logger.debug(play_result)
        play_result.show_end_message()


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        help="play the game with debug messages enabled",
        action="store_true"
    )
    return parser.parse_args()


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(fmt=logging.Formatter(
        "{levelname:s}: {asctime:s}.{msecs:.0f} - {message}",
        '%Y-%d-%m %H:%M:%S',
        "{"
    ))
    logger.addHandler(handler)
    return logger


if __name__ == "__main__":
    args = get_args()
    logger = get_logger()
    game = Game(FrenchNumberPracticeConfig())
    game.play()
