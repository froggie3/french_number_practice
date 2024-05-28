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

            coordinates = HalfOpenedInterval(start, end) \
                .limit_bottom(self.config.MIN_NUMBER) \
                .limit_top(self.config.MAX_NUMBER) \
                .to_opened_interval()
        return coordinates


class PlayingStatus:
    """
    A class that holds something related to playing status.
    """

    def __init__(self, coordinates: OpenedInterval) -> None:
        self.attempt_cumulative = 0
        self.correct_successive = 0
        self.correct_successive_history = []
        self.mistakes_count = 0
        self.solved_problems = set()
        self.time_elapsed = 10e9
        self.time_started = 0
        self.coordinates = coordinates

    def max_correct_successive(self) -> int:
        return max(self.correct_successive_history)

    def total_problems_solved(self,) -> int:
        return len(self.solved_problems)

    def count(self) -> int:
        """
        Counts the number of problem to be solved.
        """
        return self.coordinates.end - self.coordinates.start


class Timer:
    """
    A dedicated class to measure the time taken in execution of a function
    """

    def __init__(self) -> None:
        self.time_elapsed = 0.0
        self.time_started = 0.0
        self.time_stopped = 0.0

    def __timer_start(self) -> None:
        self.time_started = time()

    def __timer_stop(self) -> None:
        self.time_stopped = time()
        self.time_elapsed = self.time_stopped - self.time_started

    def measure_time_execution(self, user_function) -> float:
        self.__timer_start()
        user_function()
        self.__timer_stop()
        return self.time_elapsed

    @staticmethod
    def display_time_elapsed(time_elapsed: float) -> str:
        def calculate_time_elapsed(time_elapsed: float):
            rounded_time = int(time_elapsed)
            hour, second = divmod(rounded_time, 3600)
            minute, second = divmod(second, 60)
            milisecond = time_elapsed - rounded_time
            return hour, minute, second, milisecond
        _, minute, second, milisecond = calculate_time_elapsed(time_elapsed)
        return f"%01d:%02d.%s" % (minute, second, str(milisecond)[2:][:3])


class Play:
    """
    A set of primary routines.
    """

    def __init__(self, queue: deque, playing_status: PlayingStatus, config: Config) -> None:
        self.config: Config = config

        generate_word_range = HalfOpenedInterval(
            self.config.MIN_NUMBER,
            self.config.MAX_NUMBER
        ) \
            .to_opened_interval()

        self.french_numbers = [
            num2words(i, lang=self.config.LANGUAGE)
            for i in range(generate_word_range.start, generate_word_range.end)
        ]
        self.playing_status = playing_status
        self.queue: deque = queue

    def enable_loop(self):
        self.validator = Validator(
            InplayingValidator(self.playing_status, self.config)
        ) \
            .validator

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
            self.playing_status.correct_successive)

    def play(self):
        timer = Timer()
        self.playing_status.time_elapsed = timer.measure_time_execution(
            self.enable_loop)
        self.show_end_message()

    def show_end_message(self) -> None:
        s = self.playing_status.total_problems_solved()
        a = self.playing_status.count()

        m = self.playing_status.mistakes_count

        t = Timer.display_time_elapsed(self.playing_status.time_elapsed)
        c = self.playing_status.max_correct_successive()

        print(f"You solved all! Here's the summary:")
        print(f"  Total problems solved              {s} / {a}")
        print(f"  Total mistakes made                {m}")
        print(f"  Maximum successive correct answer  {c}")
        print(f"  Total time spent                   {t}")

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
    pass


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

    def __is_digit(self, v: str):
        return v.isdigit()

    def __is_in_range(self, v: str):
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
        self.__prepare_problem_set(self.coordinates) \
            .__shuffle()

        return deque(self.problem_set)


if __name__ == "__main__":
    config = Config()
    game = Game(config)

    coordinates = game.get_range()
    playing_status = PlayingStatus(coordinates)

    ps = ProblemSetMaker(coordinates)
    queue = ps.get_queue()

    p = Play(queue, playing_status, config)
    p.play()

    exit(0)
