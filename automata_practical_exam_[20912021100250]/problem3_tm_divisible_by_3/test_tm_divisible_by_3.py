# test_tm_divisible_by_3.py
import unittest
from tm_divisible_by_3 import TuringMachine, create_divisible_by_3_tm

class TestTuringMachineDivisibleBy3(unittest.TestCase):

    def setUp(self):
        self.tm = create_divisible_by_3_tm()

    def run_tm_test(self, input_string, expected_acceptance):
        # print(f"\nTesting TM with input: '{input_string}'") # Optional: for verbose test output
        actual_acceptance = self.tm.simulate(input_string, max_steps=200)
        
        self.assertEqual(actual_acceptance, expected_acceptance,
                         f"Input '{input_string}' failed. Expected {'Accept' if expected_acceptance else 'Reject'}, "
                         f"got {'Accept' if actual_acceptance else 'Reject'}")

    def test_accept_empty_string(self):
        self.run_tm_test("", True)

    def test_accept_zero(self):
        self.run_tm_test("0", True)

    def test_accept_three(self):
        self.run_tm_test("11", True)

    def test_accept_six(self):
        self.run_tm_test("110", True)

    def test_accept_nine(self):
        self.run_tm_test("1001", True)

    def test_accept_multiple_zeros_start(self):
        self.run_tm_test("00011", True)

    def test_reject_one(self):
        self.run_tm_test("1", False)

    def test_reject_two(self):
        self.run_tm_test("10", False)

    def test_reject_four(self):
        self.run_tm_test("100", False)

    def test_reject_five(self):
        self.run_tm_test("101", False)
        
    def test_reject_seven(self):
        self.run_tm_test("111", False)

    def test_reject_invalid_symbol_in_input(self):
        self.assertFalse(self.tm.simulate("1021"), "Should reject input with invalid symbols")

    def test_long_string_accept(self):
        self.run_tm_test("110110110", True)

    def test_long_string_reject(self):
        self.run_tm_test("110110111", False)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)