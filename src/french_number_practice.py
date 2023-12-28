#!/usr/bin/env python3.13

from collections import deque
from random import shuffle
from sys import exit
from time import time
from typing import Self

from num2words import num2words

type OpenedInterval = tuple[int, int]
type HalfOpenedInterval = tuple[int, int]
type RawInputInterval = list[str]


class Game:
    """
    A collections of general methods and settings.
    """

    MIN_NUMBER = 0
    MAX_NUMBER = 100
    LANGUAGE = "fr"
    START_INDEX = 0
    END_INDEX = 1

    def __init__(self) -> None:
        pass

    def make_range_pair(self, coordinates: HalfOpenedInterval) -> OpenedInterval:
        """
        Clips the range within range from 'Game.MAX_NUMBER' to 'Game.MAX_NUMBER',
        extending the max range by one.
        """
        return (
            max(Game.MIN_NUMBER, coordinates[Game.START_INDEX]),
            min(coordinates[Game.END_INDEX], Game.MAX_NUMBER) + 1
        )

    def get_range(self) -> RawInputInterval:
        """
        Defines a range by a user input.
        """
        print(
            "Specify the two values for the start and end of the range; \n"
            "The values must be separated by a space:"
        )
        v = ProblemSetMakerValidator()

        validated = False
        split_values = []

        while not validated:
            try:
                input_str = input("input the range [from, to]: ")
            except KeyboardInterrupt as e:
                print(e)
                exit(1)

            split_values = input_str.split()
            validated = v.is_valid(split_values)

            if not validated:
                print("Two numbers must be entered, separated by a space.")

        return split_values


class PlayData:
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

    def timer_start(self,) -> None:
        self.time_started = time()

    def timer_stop(self,) -> None:
        self.time_elapsed = time() - self.time_started

    def total_problems_solved(self,) -> int:
        return len(self.solved_problems)

    def count(self) -> int:
        """
        Counts the number of problem to be solved.
        """
        return self.coordinates[Game.END_INDEX] - self.coordinates[Game.START_INDEX]


class Play:
    """
    A set of primary routines.
    """

    def __init__(self, queue: deque, data: PlayData) -> None:
        self.french_numbers = [
            num2words(i, lang=Game.LANGUAGE)
            for i in range(Game.MIN_NUMBER, Game.MAX_NUMBER + 1)
        ]
        self.d = data
        self.queue: deque = queue

    def play(self):
        self.d.timer_start()
        self.v = Validator(data=self.d)

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
                elif not self.v.is_valid(guess):
                    continue
                elif int(guess) != correct_answer:
                    print("Guess again")
                    self.queue.appendleft(correct_answer)
                    self.d.correct_successive_history.append(
                        self.d.correct_successive
                    )
                    self.d.correct_successive = 0
                    self.d.mistakes_count += 1
                else:
                    self.say_compliment()
                    self.d.correct_successive += 1
                    self.d.solved_problems.add(correct_answer)
                    is_solved = True

                self.d.attempt_cumulative += 1
        else:
            print("You solved all! Well done.")
            self.finalize_app()

    def finalize_app(self) -> None:
        self.d.timer_stop()
        self.d.correct_successive_history.append(
            self.d.correct_successive
        )
        self.show_end_message()

    def format_time(self, t: float) -> str:
        a = int(t)
        m = a // 60
        s = a % 60
        mm = str(t - a)[2:][:3]
        return f"%d:%02d.%s" % (m, s, mm)

    def show_end_message(self) -> None:
        s = self.d.total_problems_solved()
        a = self.d.count()

        m = self.d.mistakes_count

        t = self.format_time(self.d.time_elapsed)
        c = self.d.max_correct_successive()

        print()
        print(f"Summary:")
        print(f"  Total problems solved: {s} / {a}")
        print(f"  Total mistakes made: {m}")
        print(f"  Maximum successive correct answer: {c}")
        print(f"  Total time spent: {t}")

    def say_compliment(self) -> None:
        a = self.d.correct_successive
        if a < 1:
            print("Good guess!")
            return
        print("Good guess! " f"(consecutive good answers: {a})")

    def show_correct_answer(self, correct_answer: int) -> None:
        print(f"The answer: {correct_answer}")


class Validator():
    """
    A set of validations to be enabled in playing games.
    """

    def __init__(self, data: PlayData) -> None:
        self.d = data

    def is_valid(self, input_str: str) -> bool:
        if not self.__is_digit(input_str):
            print("Please enter a number")
            return False
        if not self.__is_in_range(input_str):
            p = self.d.coordinates[Game.START_INDEX]
            q = self.d.coordinates[Game.END_INDEX]
            print(f"The value must be within a value from {p} to {q}")
            return False

        return True

    def __is_digit(self, v: str):
        return v.isdigit()

    def __is_in_range(self, v: str):
        return Game.MIN_NUMBER <= int(v) <= Game.MAX_NUMBER


class ProblemSetMakerValidator(Validator):
    """
    A set of validations needed to generate flawless problem sets.
    """

    def __init__(self) -> None:
        pass

    def is_valid(self, split_values: RawInputInterval) -> bool:
        if not self.__is_digit_all(split_values):
            print("Please enter a number")
            return False
        elif not self.__is_pair(split_values):
            return False
        elif not self.__is_in_range(split_values):
            print(
                f"Both start and end must be within a value from "
                f"{Game.MIN_NUMBER} to {Game.MAX_NUMBER}"
            )
            return False
        elif not self.__is_in_range2(split_values):
            print("Start must be less than or equal to end")
            return False
        return True

    def __is_pair(self, v: RawInputInterval) -> bool:
        range_pair = self.__make_range_pair(v)
        return len(range_pair) == 2

    def __is_digit_all(self, v: RawInputInterval) -> bool:
        return all([v.isdigit() for v in v])

    def __is_in_range(self, v: RawInputInterval) -> bool:
        start, end = self.__make_range_pair(v)
        return (Game.MIN_NUMBER <= start <= Game.MAX_NUMBER and Game.MIN_NUMBER <= end <= Game.MAX_NUMBER)

    def __is_in_range2(self, v: RawInputInterval) -> bool:
        start, end = self.__make_range_pair(v)
        return start < end

    def __make_range_pair(self, v: RawInputInterval) -> OpenedInterval:
        return tuple(map(int, v))


class ProblemSetMaker():
    """
    Generates a set of numbers.
    """

    def __init__(self, coordinates: OpenedInterval) -> None:
        self.coordinates = coordinates
        self.problem_set = []

    def __prepare_problem_set(self, coordinates: OpenedInterval) -> Self:
        start, end = coordinates
        self.problem_set = list(range(start, end))
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
    g = Game()

    coordinates: HalfOpenedInterval = tuple(int(x) for x in g.get_range())
    coordinates_new = g.make_range_pair(coordinates)
    data = PlayData(coordinates=coordinates_new)

    ps = ProblemSetMaker(data.coordinates)
    queue = ps.get_queue()

    p = Play(queue, data)
    p.play()

    exit(0)
