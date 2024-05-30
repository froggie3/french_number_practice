#!/usr/bin/env python3.13

from french_number_practice import *
import unittest


class TestValidator(unittest.TestCase):

    def test_is_digit(self):
        v = Validator(PlayingStatus((0, 101)))
        tests = (
            "-99",
            "0.1",
            "2e8",
        )
        for test in tests:
            self.assertFalse(v._Validator__is_digit(test))

    def test_is_in_range(self):
        v = Validator(PlayingStatus((0, 101)))
        tests = (
            "999",
            "-99",
        )
        for test in tests:
            self.assertFalse(v._Validator__is_in_range(test))


class TestProblemSetMakerValidator(unittest.TestCase):

    def test_pair(self):
        v = ProblemBuilderFrenchValidator()
        tests = (
            ["0"],
            ["1", "2", "3"],
        )
        for test in tests:
            self.assertFalse(
                v._ProblemSetMakerValidator__is_pair(test)
            ),

    def test_is_digit_all(self):
        v = ProblemBuilderFrenchValidator()
        tests = (
            ["a", "b"],
            ["0", "-1"],
            ["0", "1e9"],
            ["0", "2.2"],
        )
        for test in tests:
            self.assertFalse(
                v._ProblemSetMakerValidator__is_digit_all(test)
            )

    def test_is_in_range(self):
        v = ProblemBuilderFrenchValidator()
        tests = (
            ["0", "99999"],
        )
        for test in tests:
            self.assertFalse(
                v._ProblemSetMakerValidator__is_in_range(test)
            ),

    def test_is_in_range2(self):
        v = ProblemBuilderFrenchValidator()
        tests = (
            ["99999", "0"],
        )
        for test in tests:
            self.assertFalse(
                v._ProblemSetMakerValidator__is_in_range2(test)
            ),

    def test_make_range_pair(self):
        v = ProblemBuilderFrenchValidator()
        tests = (
            (["33", "66"], (33, 66)),
        )
        for test in tests:
            self.assertEqual(
                v._ProblemSetMakerValidator__make_range_pair(test[0]),
                test[1]
            ),


class TestGame(unittest.TestCase):

    def test_make_range_pair(self):
        tests = (
            ((0, 1), (0, 2)),
        )
        for test in tests:
            a = Game()
            self.assertEqual(
                a.make_range_pair(test[0]),
                test[1]
            )


class TestProblemSetMaker(unittest.TestCase):

    def test_prepare_problem_set(self):
        tests = (
            ((20, 31), 11),
        )
        for test in tests:
            a = ProblemBuilderFrench(test)
            a._ProblemSetMaker__prepare_problem_set(test[0])
            self.assertEqual(len(a.problem_set), test[1])

    def test_get_queue_returns_deque(self):
        tests = (
            (20, 40),
        )
        for test in tests:
            a = ProblemBuilderFrench(test)
            self.assertEqual(
                str(type(a.get_queue())),
                "<class 'collections.deque'>"
            )

    def test_get_queue(self):
        tests = (
            (20, 40),
        )
        # is properly shuffled?
        for test in tests:
            a = ProblemBuilderFrench(test)
            q = list(a.get_queue())
            ok = False
            for i in range(test[1] - test[0]):
                if q[i] != i:
                    ok = True
                    break
            self.assertEqual(ok, True)


if __name__ == '__main__':
    unittest.main()
