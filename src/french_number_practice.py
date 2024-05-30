#!/usr/bin/env python3.13

from collections import deque
from random import shuffle
from sys import exit
from time import time
from typing import Self
from num2words import num2words


class Config:
    def __init__(self) -> None:
        self.MIN_NUMBER = 0
        self.MAX_NUMBER = 100
        self.LANGUAGE = "fr"


class Interval:
    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end

    def limit_bottom(self, x: int) -> Self:
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

    def limit_top(self, x: int) -> Self:
        """
        limit the end value to x.
              ___
             /^------ x
            /
           /
        ~~~~~~
        """
        self.end = min(self.end, x)
        return self


class OpenedInterval(Interval):
    def to_half_opened_interval(self):
        return HalfOpenedInterval(self.start, self.end - 1)


class HalfOpenedInterval(Interval):
    def to_opened_interval(self):
        return OpenedInterval(self.start, self.end + 1)


def validate_range_partial(coordinates: OpenedInterval):
    def validate_range(test_string: str):
        if coordinates.start <= int(test_string) <= coordinates.end:
            return
        raise ValueError("The value must be within a value from {0:d} to {1:d}".format(
            coordinates.start,
            coordinates.end
        ))
    return validate_range


def try_int_conversion(test_string: str):
    try:
        int(test_string)
    except ValueError:
        raise ValueError("Please enter a number")


class TimerResult:
    def __init__(self, seconds: float) -> None:
        self.seconds = seconds

    def display_time_elapsed(self):
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

    def start(self) -> Self:
        self.started_seconds = time()
        return self

    def stop(self) -> Self:
        self.elapsed_seconds = time() - self.started_seconds
        return self

    def execute(self, user_function) -> Self:
        user_function()
        return self

    def retrieve_result(self) -> TimerResult:
        return TimerResult(self.elapsed_seconds)


class PlayingStatus:
    """
    A class that holds something related to playing status.
    """

    def __init__(self, queue, timer: Timer) -> None:
        self.attempts_count = 0
        self.correct_successive_count = 0
        self.correct_successive_count_max = 0
        self.mistakes_count = 0
        self.queue_length = len(queue)
        self.timer = timer
        self.timer_result = TimerResult(0.0)

    def __solved(self):
        self.attempts_count += 1
        self.correct_successive_count_max = max(
            self.correct_successive_count_max, self.correct_successive_count
        )

    def correct(self):
        """Process on correct answer"""
        self.correct_successive_count += 1
        self.__solved()

    def wrong(self):
        """Process on wrong answer"""
        self.correct_successive_count = 0
        self.mistakes_count += 1
        self.__solved()

    def show_end_message(self) -> None:
        lines = [
            "{0:<50} {1} / {2}".format(
                "Total problems solved (actually / originally)",
                self.attempts_count - self.mistakes_count,
                self.queue_length
            ),
            "{0:<50} {1}".format(
                "Total mistakes made",
                self.mistakes_count
            ),
            "{0:<50} {1}".format(
                "Maximum successive correct answer",
                self.correct_successive_count_max
            ),
            "{0:<50} {1}".format(
                "Total time spent",
                self.timer_result.display_time_elapsed()
            ),
        ]

        print("You solved all! Here's the summary:")
        for line in lines:
            print(f"  {line}")


class Validator:
    def __init__(self, validator) -> None:
        self.validator = validator


class InplayingValidator:
    """
    A set of validations to be enabled in playing games.
    """

    def __init__(self, config: Config, *user_functions) -> None:
        self.config = config
        self.user_functions = user_functions

    def is_valid(self, input_str: str):
        try:
            for user_func in self.user_functions:
                user_func(input_str)
        except ValueError as e:
            print(e)
            return False
        return True


class ProblemSetMakerValidator:
    """
    A set of validations needed to generate flawless problem sets.
    """

    def __init__(self, coordinates: Interval, config: Config) -> None:
        self.coordinates = coordinates
        self.config = config

    def is_valid(self):
        if not self.__is_in_range():
            raise ValueError("Both start and end must be within a value from {0:d} to {1:d}".format(
                self.config.MIN_NUMBER,
                self.config.MAX_NUMBER
            ))
        elif not self.__is_in_range2():
            raise ValueError("Start must be less than or equal to end")

    def __is_in_range(self) -> bool:
        return (
            self.config.MIN_NUMBER <= self.coordinates.start <= self.config.MAX_NUMBER and
            self.config.MIN_NUMBER <= self.coordinates.end <= self.config.MAX_NUMBER
        )

    def __is_in_range2(self) -> bool:
        return self.coordinates.start < self.coordinates.end


class Card:
    def __init__(self):
        self.mistakes = 0
        self.problem = ""
        self.answer = ""


class NumberFrenchCard:
    def __init__(self, problem: str, answer: str):
        self.problem = problem
        self.answer = answer

    def __repr__(self):
        return f"{__class__.__name__}{self.problem, self.answer}"


class ProblemBuilder:
    pass


class ProblemBuilderFrench(ProblemBuilder):
    """
    Generates a set of numbers.
    """

    def __init__(self, coordinates: OpenedInterval, config: Config) -> None:
        self.problem_set = []
        self.coordinates = coordinates
        self.config = config

    def get_queue(self) -> deque:
        """
        Get a queue of sets of problem, which is shuffled.
        """

        for n in range(self.coordinates.start, self.coordinates.end):
            self.problem_set.append(NumberFrenchCard(
                num2words(n, lang=self.config.LANGUAGE),
                str(n),
            ))

        shuffle(self.problem_set)
        return deque(self.problem_set)


class Play:
    """
    A set of primary routines.
    """

    def __init__(self, queue: deque, playing_status: PlayingStatus, validator: InplayingValidator) -> None:
        self.queue = queue
        self.playing_status = playing_status
        self.validator = validator

    def enable_loop(self):
        while self.queue:
            card = self.queue.pop()
            is_solved = False

            assert (isinstance(card, NumberFrenchCard))

            while not is_solved:
                display = card.problem
                try:
                    guess = input(f"{display}: ")
                except (KeyboardInterrupt, EOFError) as e:
                    print(e)
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

    def play(self) -> PlayingStatus:
        self.playing_status.timer_result = self.playing_status.timer.start(
        ).execute(
            self.enable_loop
        ).stop(
        ).retrieve_result()

        return self.playing_status

    def say_compliment(self) -> None:
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

    def __init__(self, config: Config) -> None:
        self.config = config

    def get_cordinates_input(self) -> OpenedInterval:
        """
        Defines a range by a user input.
        """
        print(
            "Specify the two values for the start and end of the range; \n"
            "The values must be separated by a space:"
        )

        validated = False
        coordinates_half_open = HalfOpenedInterval(-1, -1)

        while not validated:
            try:
                input_str = input("Input the range [from, to]: ")
            except (KeyboardInterrupt, EOFError) as e:
                print(e)
                exit(1)

            split_values = input_str.split()

            try:
                if not len(split_values) == 2:
                    raise ValueError(
                        "Two numbers must be entered, separated by a space."
                    )

                for try_string in split_values:
                    try_int_conversion(try_string)

            except ValueError as e:
                print(e)
                continue

            start, end = [int(x) for x in split_values]
            coordinates_half_open = HalfOpenedInterval(start, end)

            try:
                Validator(
                    ProblemSetMakerValidator(
                        coordinates_half_open,
                        self.config
                    )
                ).validator.is_valid()

            except ValueError as e:
                print(e)
                continue

            validated = True

        coordinates = coordinates_half_open.limit_bottom(
            self.config.MIN_NUMBER
        ).limit_top(
            self.config.MAX_NUMBER
        ).to_opened_interval()

        return coordinates

    def play(self) -> None:
        coordinates = self.get_cordinates_input()
        queue = ProblemBuilderFrench(
            coordinates,
            self.config
        ).get_queue()

        validator = Validator(
            InplayingValidator(
                self.config,
                try_int_conversion,
                validate_range_partial(coordinates)
            )
        ).validator

        p = Play(
            queue,
            PlayingStatus(
                queue,
                Timer(),
            ),
            validator,
        )

        play_result = p.play()
        play_result.show_end_message()


if __name__ == "__main__":
    game = Game(Config())
    game.play()
