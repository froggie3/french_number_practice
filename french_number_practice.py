#!/usr/bin/env python3

import sys
from time import time
from collections import deque
from random import shuffle
from typing import Tuple


class PlayData:
    attempt_cumulative = 0
    correct_successive = 0
    correct_successive_history = []
    mistakes_count = 0
    solved_problems = set()
    time_elapsed = 10e9
    time_started = 0

    def max_correct_successive(self,):
        return max(self.correct_successive_history)

    def problems_count(self, start, end):
        return end - start

    def timer_start(self,):
        self.time_started = time()

    def timer_stop(self,):
        self.time_elapsed = time() - self.time_started
        # print(f"{self.time_started=}")
        # print(f"{self.time_elapsed=}")

    def total_problems_solved(self,):
        return len(self.solved_problems)


def validate_range(start: int, end: int) -> Tuple[int, int]:
    interrupt = False
    if not (0 <= start <= 100 and 0 <= end <= 100):
        print("both start and end must be within a value from 0 to 100")
        interrupt = True
    if start > end:
        print("start must be less than or equal to end")
        interrupt = True
    if interrupt:
        sys.exit(1)
    return max(0, start), min(end, len(french_numbers)) + 1


def isdigit_wrapper(input_str: str) -> bool:
    if input_str.isdigit():
        return True
    print("please enter a number")
    return False


def problem_validate_range(input_str: str) -> bool:
    if start <= int(input_str) < end:
        return True
    print(f"the value must be within a value from {start} to {end}")
    return False


def show_end_message() -> None:
    print()
    print("total problems solved: "
          f"{pdata.total_problems_solved()} / {pdata.problems_count(start, end)}")
    print(f"total mistakes made: {pdata.mistakes_count}")
    print(f"maximum successive correct answer: "
          f"{pdata.max_correct_successive()}")
    print(f"total time spent: {pdata.time_elapsed}")


def say_compliment():
    if pdata.correct_successive < 1:
        print("good guess!")
    else:
        print("good guess! "
              f"(consecutive good answers: {pdata.correct_successive})")


def show_correct_answer(correct_answer: int) -> None:
    print(f"the answer: {correct_answer}")


def finalize_app() -> None:
    pdata.timer_stop()
    pdata.correct_successive_history.append(pdata.correct_successive)
    show_end_message()


if __name__ == "__main__":
    french_numbers = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt", "vingt et un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf", "trente", "trente et un", "trente-deux", "trente-trois", "trente-quatre", "trente-cinq", "trente-six", "trente-sept", "trente-huit", "trente-neuf", "quarante", "quarante et un", "quarante-deux", "quarante-trois", "quarante-quatre", "quarante-cinq", "quarante-six", "quarante-sept", "quarante-huit", "quarante-neuf", "cinquante", "cinquante et un", "cinquante-deux", "cinquante-trois", "cinquante-quatre", "cinquante-cinq", "cinquante-six", "cinquante-sept", "cinquante-huit", "cinquante-neuf",
                      "soixante", "soixante et un", "soixante-deux", "soixante-trois", "soixante-quatre", "soixante-cinq", "soixante-six", "soixante-sept", "soixante-huit", "soixante-neuf", "soixante-dix", "soixante et onze", "soixante-douze", "soixante-treize", "soixante-quatorze", "soixante-quinze", "soixante-seize", "soixante-dix-sept", "soixante-dix-huit", "soixante-dix-neuf", "quatre-vingt", "quatre-vingt-un", "quatre-vingt-deux", "quatre-vingt-trois", "quatre-vingt-quatre", "quatre-vingt-cinq", "quatre-vingt-six", "quatre-vingt-sept", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-dix", "quatre-vingt et onze", "quatre-vingt-douze", "quatre-vingt-treize", "quatre-vingt-quatorze", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-dix-sept", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "cent"]

    print("specify the two values for the start and end of the range; \n"
          "the values must be separated by a space:")
    while True:
        try:
            input_str = input("input the range [from, to]: ")
        except KeyboardInterrupt as e:
            print(e)
            sys.exit(1)

        split_values = input_str.split()
        if not all([v.isdigit() for v in split_values]):
            print("please enter a number")
            continue

        if len(range_pair := list(map(int, split_values))) == 2:
            break
        else:
            print("please try again;\n"
                  "two numbers must be entered, separated by a space.")

    start, end = validate_range(*range_pair)
    pdata = PlayData()
    problem_set = list(range(start, end))
    shuffle(problem_set)
    queue = deque(problem_set)

    pdata.timer_start()
    while queue:
        correct_answer = queue.pop()
        is_solved = False
        while not is_solved:
            try:
                guess = input(f"{french_numbers[correct_answer]}: ")
            except KeyboardInterrupt as e:
                print(e)
                show_correct_answer(correct_answer)
                finalize_app()
                sys.exit(0)
            if guess == "quit":
                queue.appendleft(correct_answer)
                show_correct_answer(correct_answer)
                break
            elif not (isdigit_wrapper(guess) or problem_validate_range(guess)):
                continue
            elif int(guess) != correct_answer:
                print("guess again")
                queue.appendleft(correct_answer)
                pdata.correct_successive_history.append(
                    pdata.correct_successive)
                pdata.correct_successive = 0
                pdata.mistakes_count += 1
            else:
                say_compliment()
                pdata.correct_successive += 1
                pdata.solved_problems.add(correct_answer)
                is_solved = True
            pdata.attempt_cumulative += 1
    else:
        print("you solved all! well done.")
        finalize_app()
    sys.exit(0)
