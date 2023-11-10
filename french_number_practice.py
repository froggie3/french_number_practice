#!/usr/bin/env python3

import random


def validate_range(start, end):
    if start < 0:
        print("start must be non-negative")
        exit()
    if end < 0:
        print("end must be non-negative")
        exit()
    if start > end:
        print("start must be less than or equal to end")
        exit()
    return max(0, start), min(end, len(french))


def validate_input(input_str):
    if not input_str.isdigit():
        print("please input the valid number")
        return False
    return int(input_str) >= start and int(input_str) <= end


def give_up(correct):
    print(f"the answer: {correct}")


french = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt", "vingt et un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf", "trente", "trente et un", "trente-deux", "trente-trois", "trente-quatre", "trente-cinq", "trente-six", "trente-sept", "trente-huit", "trente-neuf", "quarante", "quarante et un", "quarante-deux", "quarante-trois", "quarante-quatre", "quarante-cinq", "quarante-six", "quarante-sept", "quarante-huit", "quarante-neuf", "cinquante", "cinquante et un", "cinquante-deux", "cinquante-trois", "cinquante-quatre", "cinquante-cinq", "cinquante-six", "cinquante-sept", "cinquante-huit", "cinquante-neuf",
          "soixante", "soixante et un", "soixante-deux", "soixante-trois", "soixante-quatre", "soixante-cinq", "soixante-six", "soixante-sept", "soixante-huit", "soixante-neuf", "soixante-dix", "soixante et onze", "soixante-douze", "soixante-treize", "soixante-quatorze", "soixante-quinze", "soixante-seize", "soixante-dix-sept", "soixante-dix-huit", "soixante-dix-neuf", "quatre-vingt", "quatre-vingt-un", "quatre-vingt-deux", "quatre-vingt-trois", "quatre-vingt-quatre", "quatre-vingt-cinq", "quatre-vingt-six", "quatre-vingt-sept", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-dix", "quatre-vingt et onze", "quatre-vingt-douze", "quatre-vingt-treize", "quatre-vingt-quatorze", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-dix-sept", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "cent", ]

try:
    start, end = map(int, input("input the range to ask (from, to]: ").split())
except KeyboardInterrupt:
    pass

start, end = validate_range(start, end)
problems = end - start
correct_successive = 0
correct_cumulative = 0
attempt_cumulative = 0
solved = [False] * end

try:
    while correct_cumulative < problems:
        correct = random.randint(start, end - 1)
        if solved[correct]:
            continue
        not_valid = True
        while not_valid:
            guess = input(f"{french[correct]}: ")
            if guess == "quit":
                solved[correct] = True
                give_up(correct)
                break
            elif not validate_input(guess):
                continue
            elif int(guess) != correct:
                print("guess again")
                correct_successive = 0
            else:
                print("good guess!" if correct_successive <
                      1 else f"good guess! (consecutive good answers: {correct_successive})")
                solved[correct] = True
                correct_successive += 1
                correct_cumulative += 1
                not_valid = False
            attempt_cumulative += 1
    else:
        print("You solved all! well done.")
except KeyboardInterrupt:
    print()
    give_up(correct)
