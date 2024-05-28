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
    ステートレスにしたい！
    """

    def __init__(self, coordinates: OpenedInterval, timer: Timer) -> None:
        self.attempt_cumulative = 0
        self.correct_successive = 0
        self.correct_successive_history = []
        self.mistakes_count = 0
        self.solved_problems = set()
        self.time_elapsed = 10e9
        self.time_started = 0
        self.coordinates = coordinates
        self.timer = timer
        self.timer_result = TimerResult(0.0)

    def count(self) -> int:
        """
        Counts the number of problem to be solved.
        """
        return self.coordinates.end - self.coordinates.start

    def show_end_message(self) -> None:
        lines = [
            "{0:<40} {1} / {2}".format(
                "Total problems solved",
                len(self.solved_problems),
                self.count()
            ),
            "{0:<40} {1}".format(
                "Total mistakes made",
                self.mistakes_count
            ),
            "{0:<40} {1}".format(
                "Maximum successive correct answer",
                max(self.correct_successive_history)
            ),
            "{0:<40} {1}".format(
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

    def __init__(self, coordinates: OpenedInterval, config: Config) -> None:
        self.coordinates = coordinates
        self.config = config

    def is_valid(self, input_str: str):
        try:
            try:
                int(input_str)
            except ValueError:
                raise ValueError("Please enter a number")

            if not self.coordinates.start <= int(input_str) <= self.coordinates.end:
                raise ValueError("The value must be within a value from {0:d} to {1:d}".format(
                    self.coordinates.start,
                    self.coordinates.end
                ))
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
            raise ValueError("Both start and end must be within a value from {0:s} to {1:s}".format(
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


class ProblemSetMaker():
    """
    Generates a set of numbers.
    """

    def __init__(self, coordinates: OpenedInterval) -> None:
        self.coordinates = coordinates
        self.problem_set = []

    def __prepare_problem_set(self, coordinates: OpenedInterval) -> Self:
        self.problem_set = list(range(coordinates.start, coordinates.end))
        return self

    def __shuffle(self) -> Self:
        shuffle(self.problem_set)
        return self

    def get_queue(self) -> deque:
        """
        Get a queue of sets of problem, which is shuffled.
        """
        self.__prepare_problem_set(
            self.coordinates
        ).__shuffle()

        return deque(self.problem_set)


class Play:
    """
    A set of primary routines.
    """

    def __init__(self, queue: deque, playing_status: PlayingStatus, validator: InplayingValidator, french_numbers: list) -> None:
        self.queue = queue
        self.playing_status = playing_status
        self.validator = validator
        self.french_numbers = french_numbers

    def enable_loop(self):
        while self.queue:
            correct_answer = self.queue.pop()
            is_solved = False

            while not is_solved:
                try:
                    display = self.french_numbers[correct_answer]
                    guess = input(f"{display}: ")
                except KeyboardInterrupt as e:
                    print(e)
                    self.show_correct_answer(correct_answer)
                    return

                if guess == "quit":
                    self.queue.appendleft(correct_answer)
                    self.show_correct_answer(correct_answer)
                    break
                elif not self.validator.is_valid(guess):
                    continue
                elif int(guess) != correct_answer:
                    print("Guess again")
                    self.queue.appendleft(correct_answer)
                    self.playing_status.correct_successive_history.append(
                        self.playing_status.correct_successive
                    )
                    self.playing_status.correct_successive = 0
                    self.playing_status.mistakes_count += 1
                else:
                    self.say_compliment()
                    self.playing_status.correct_successive += 1
                    self.playing_status.solved_problems.add(correct_answer)
                    is_solved = True

                self.playing_status.attempt_cumulative += 1
        self.playing_status.correct_successive_history.append(
            self.playing_status.correct_successive
        )

    def play(self) -> PlayingStatus:
        self.playing_status.timer_result = self.playing_status.timer.start(
        ).execute(
            self.enable_loop
        ).stop(
        ).retrieve_result()

        return self.playing_status

    def say_compliment(self) -> None:
        if self.playing_status.correct_successive < 1:
            print("Good guess!")
            return
        print("Good guess! (consecutive good answers: {0:<d})".format(
            self.playing_status.correct_successive
        ))

    def show_correct_answer(self, correct_answer: int) -> None:
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
            except KeyboardInterrupt as e:
                print(e)
                exit(1)

            split_values = input_str.split()

            try:
                if not len(split_values) == 2:
                    raise ValueError(
                        "Two numbers must be entered, separated by a space."
                    )
                elif not all([v.isdigit() for v in split_values]):
                    raise ValueError(
                        "Please enter a number"
                    )
            except ValueError as e:
                print(e)
                continue

            start, end = [int(x) for x in split_values]
            coordinates_half_open = HalfOpenedInterval(start, end)

            try:
                Validator(ProblemSetMakerValidator(
                    coordinates_half_open,
                    self.config
                )).validator.is_valid()

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

    def prepare_french_numbers(self, coodinates: OpenedInterval) -> list:
        return [
            num2words(i, lang=self.config.LANGUAGE)
            for i in range(coodinates.start, coodinates.end)
        ]

    def play(self) -> None:
        coordinates = self.get_cordinates_input()

        p = Play(
            ProblemSetMaker(coordinates).get_queue(),
            PlayingStatus(coordinates, Timer(),),
            Validator(InplayingValidator(coordinates, self.config)).validator,
            self.prepare_french_numbers(coordinates),
        )

        play_result = p.play()
        play_result.show_end_message()


if __name__ == "__main__":
    game = Game(Config())
    game.play()

    exit(0)
