#!/usr/bin/env python3

import sys
import random
from typing import List, Tuple

from collections import deque


def validate_range(start: int, end: int) -> Tuple[int, int]:
    if start < 0:
        print("start must be non-negative")
        sys.exit(1)
    if end < 0:
        print("end must be non-negative")
        sys.exit(1)
    if start > end:
        print("start must be less than or equal to end")
        sys.exit(1)
    return max(0, start), min(end, len(french_numbers))


def validate_input(input_str: str) -> bool:
    if not input_str.isdigit():
        print("please input the valid number")
        return False
    return int(input_str) >= start and int(input_str) <= end


def give_up(correct_answer: int) -> None:
    print(f"the answer: {correct_answer}")


def prepare_problem_set() -> List[int]:
    added = [False] * french_numbers_count
    problem_set = []
    added_count = 0
    while added_count < problems_count:
        problem = random.randint(start, end - 1)
        if not added[problem]:
            problem_set.append(problem)
            added[problem] = True
            added_count += 1
    return problem_set


if __name__ == "__main__":

    french_numbers = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt", "vingt et un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf", "trente", "trente et un", "trente-deux", "trente-trois", "trente-quatre", "trente-cinq", "trente-six", "trente-sept", "trente-huit", "trente-neuf", "quarante", "quarante et un", "quarante-deux", "quarante-trois", "quarante-quatre", "quarante-cinq", "quarante-six", "quarante-sept", "quarante-huit", "quarante-neuf", "cinquante", "cinquante et un", "cinquante-deux", "cinquante-trois", "cinquante-quatre", "cinquante-cinq", "cinquante-six", "cinquante-sept", "cinquante-huit", "cinquante-neuf",
                      "soixante", "soixante et un", "soixante-deux", "soixante-trois", "soixante-quatre", "soixante-cinq", "soixante-six", "soixante-sept", "soixante-huit", "soixante-neuf", "soixante-dix", "soixante et onze", "soixante-douze", "soixante-treize", "soixante-quatorze", "soixante-quinze", "soixante-seize", "soixante-dix-sept", "soixante-dix-huit", "soixante-dix-neuf", "quatre-vingt", "quatre-vingt-un", "quatre-vingt-deux", "quatre-vingt-trois", "quatre-vingt-quatre", "quatre-vingt-cinq", "quatre-vingt-six", "quatre-vingt-sept", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-dix", "quatre-vingt et onze", "quatre-vingt-douze", "quatre-vingt-treize", "quatre-vingt-quatorze", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-dix-sept", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "cent"]
    french_numbers_count = len(french_numbers)

    try:
        s = input("input the range to ask [from, to): ")
    except KeyboardInterrupt as e:
        print(e)
        sys.exit(1)

    start, end = validate_range(*map(int, s.split()))
    problems_count = end - start
    correct_successive = 0
    correct_cumulative = 0
    attempt_cumulative = 0
    queue = deque(prepare_problem_set())

    while queue:
        correct_answer = queue.pop()
        solved = False
        while not solved:
            try:
                guess = input(f"{french_numbers[correct_answer]}: ")
            except KeyboardInterrupt as e:
                print(e)
                give_up(correct_answer)
                sys.exit(0)
            if guess == "quit":
                queue.appendleft(correct_answer)
                give_up(correct_answer)
                break
            elif not validate_input(guess):
                print(f"the value is out of range!")
                continue
            elif int(guess) != correct_answer:
                print("guess again")
                queue.appendleft(correct_answer)
                correct_successive = 0
            else:
                print("good guess!" if correct_successive < 1 else
                      f"good guess! (consecutive good answers: {correct_successive})")
                correct_successive += 1
                correct_cumulative += 1
                solved = True
            attempt_cumulative += 1
    else:
        print("You solved all! well done.")

    sys.exit(0)
