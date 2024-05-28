#!/usr/bin/env python3.13

from collections import deque
from random import shuffle
from sys import exit
from time import time
from typing import Self

from num2words import num2words


class Interval:
    start = -1
    end = -1

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
    pass


class HalfOpenedInterval(Interval):
    def to_opened_interval(self):
        return OpenedInterval(self.start, self.end + 1)


class Config:
    def __init__(self) -> None:
        self.MIN_NUMBER = 0
        self.MAX_NUMBER = 100
        self.LANGUAGE = "fr"


class Game:
    """
    A collections of general methods and settings.
    """

    def __init__(self, config: Config) -> None:
        self.config = config

    def get_range(self) -> OpenedInterval:
        """
        Defines a range by a user input.
        """
        print(
            "Specify the two values for the start and end of the range; \n"
            "The values must be separated by a space:"
        )

        validated = False
        split_values = []
        start, end = -1, -1

        while not validated:
            try:
                input_str = input("Input the range [from, to]: ")
            except KeyboardInterrupt as e:
                print(e)
                exit(1)

            split_values = input_str.split()

            if not len(split_values) == 2:
                print("Two numbers must be entered, separated by a space.")
                continue
            elif not all([v.isdigit() for v in split_values]):
                print("Please enter a number")
                continue

            start, end = [int(x) for x in split_values]
            coordinates = HalfOpenedInterval(start, end)

            validator = Validator(ProblemSetMakerValidator(coordinates, self.config)) \
                .validator

            validated = validator.is_valid()

            coordinates = HalfOpenedInterval(
                start, end
            ).limit_bottom(
                self.config.MIN_NUMBER
            ).limit_top(
                self.config.MAX_NUMBER
            ).to_opened_interval()
        return coordinates


class TimerResult:
    def __init__(self, time_elapsed: float) -> None:
        self.time_elapsed = time_elapsed

    def __calculate_time_elapsed(self):
        rounded_time = int(self.time_elapsed)
        self.hour, self.second = divmod(rounded_time, 3600)
        self.minute, self.second = divmod(self.second, 60)
        self.milisecond = self.time_elapsed - rounded_time
        return Self

    def display_time_elapsed(self) -> str:
        self.__calculate_time_elapsed()
        return f"%01d:%02d.%.3f" % (
            self.minute, self.second, self.milisecond
        )


class Timer:
    """
    A dedicated class to measure the time taken in execution of a function
    """

    def __init__(self) -> None:
        self.time_elapsed = 0.0
        self.time_started = 0.0

    def start(self) -> Self:
        self.time_started = time()
        return self

    def stop(self) -> Self:
        self.time_elapsed = time() - self.time_started
        return self

    def execute(self, user_function) -> Self:
        user_function()
        return self

    def retrieve_result(self) -> TimerResult:
        return TimerResult(self.time_elapsed)


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


class Play:
    """
    A set of primary routines.
    """

    def __init__(self, queue: deque, playing_status: PlayingStatus, config: Config) -> None:
        self.config: Config = config

        generate_word_range = HalfOpenedInterval(
            self.config.MIN_NUMBER,
            self.config.MAX_NUMBER
        ).to_opened_interval()

        self.french_numbers = [
            num2words(i, lang=self.config.LANGUAGE)
            for i in range(generate_word_range.start, generate_word_range.end)
        ]
        self.playing_status = playing_status
        self.queue: deque = queue

    def enable_loop(self):
        self.validator = Validator(
            InplayingValidator(self.playing_status, self.config)
        ).validator

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
                    self.finalize_app()
                    exit(0)

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

    def play(self):
        self.playing_status.timer_result = self.playing_status.timer.start(
        ).execute(
            self.enable_loop
        ).stop(
        ).retrieve_result()
        self.playing_status.show_end_message()

    def get_playing_result(self):
        return self.playing_status

    def say_compliment(self) -> None:
        a = self.playing_status.correct_successive
        if a < 1:
            print("Good guess!")
            return
        print("Good guess! " f"(consecutive good answers: {a})")

    def show_correct_answer(self, correct_answer: int) -> None:
        print(f"The answer: {correct_answer}")

    def finalize_app(self):
        pass


class Validator():
    def __init__(self, validator) -> None:
        self.validator = validator


class InplayingValidator:
    """
    A set of validations to be enabled in playing games.
    """

    def __init__(self, data: PlayingStatus, config: Config) -> None:
        self.d = data
        self.config = config

    def is_valid(self, input_str: str) -> bool:
        if not self.__is_digit(input_str):
            print("Please enter a number")
            return False
        if not self.__is_in_range(input_str):
            p = self.d.coordinates.start
            q = self.d.coordinates.end
            print(f"The value must be within a value from {p} to {q}")
            return False

        return True

    def __is_digit(self, v: str) -> bool:
        return v.isdigit()

    def __is_in_range(self, v: str) -> bool:
        return self.config.MIN_NUMBER <= int(v) <= self.config.MAX_NUMBER


class ProblemSetMakerValidator:
    """
    A set of validations needed to generate flawless problem sets.
    """

    def __init__(self, coordinates: Interval, config: Config) -> None:
        self.coordinates = coordinates
        self.config = config

    def is_valid(self) -> bool:
        if not self.__is_in_range():
            print(
                f"Both start and end must be within a value from "
                f"{self.config.MIN_NUMBER} to {self.config.MAX_NUMBER}"
            )
            return False
        elif not self.__is_in_range2():
            print("Start must be less than or equal to end")
            return False

        return True

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


if __name__ == "__main__":
    config = Config()
    game = Game(config)

    coordinates = game.get_range()
    playing_status = PlayingStatus(coordinates, Timer())

    ps = ProblemSetMaker(coordinates)
    queue = ps.get_queue()

    p = Play(queue, playing_status, config)
    p.play()

    exit(0)
