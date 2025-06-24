import unittest
from utils import calculate_net_profit_percentage

class TestCalculateNetProfitPercentage(unittest.TestCase):

    def test_positive_profit_simple(self):
        # Simple case: initial 100, current 110 -> 0.10
        self.assertAlmostEqual(calculate_net_profit_percentage(100, 110), 0.10)

    def test_positive_profit_larger_numbers(self):
        # Larger numbers: initial 50000, current 75000 -> 0.50
        self.assertAlmostEqual(calculate_net_profit_percentage(50000, 75000), 0.50)

    def test_loss_scenario_simple(self):
        # Simple case: initial 100, current 90 -> -0.10
        self.assertAlmostEqual(calculate_net_profit_percentage(100, 90), -0.10)

    def test_loss_scenario_larger_numbers(self):
        # Larger loss: initial 2000, current 500 -> -0.75
        self.assertAlmostEqual(calculate_net_profit_percentage(2000, 500), -0.75)

    def test_break_even_scenario(self):
        # Break-even: initial 100, current 100 -> 0.0
        self.assertAlmostEqual(calculate_net_profit_percentage(100, 100), 0.0)

    def test_initial_investment_zero(self):
        # Initial investment is 0 (should raise ValueError)
        with self.assertRaisesRegex(ValueError, "Initial investment must be greater than zero."):
            calculate_net_profit_percentage(0, 100)

    def test_initial_investment_negative(self):
        # Initial investment is negative (should raise ValueError)
        with self.assertRaisesRegex(ValueError, "Initial investment must be greater than zero."):
            calculate_net_profit_percentage(-100, 100)

    def test_current_value_zero_positive_initial(self):
        # Current value is 0, initial is positive: initial 100, current 0 -> -1.0
        self.assertAlmostEqual(calculate_net_profit_percentage(100, 0), -1.0)

    def test_large_numbers_precision(self):
        # Test with large numbers that might have precision issues
        self.assertAlmostEqual(calculate_net_profit_percentage(1234567.89, 9876543.21), 7.000000, places=5) # Expected: (9876543.21 - 1234567.89) / 1234567.89

    def test_small_numbers_precision(self):
        # Test with small numbers that might have precision issues
        self.assertAlmostEqual(calculate_net_profit_percentage(0.1, 0.11), 0.1, places=5) # Expected: (0.11 - 0.1) / 0.1

if __name__ == '__main__':
    unittest.main()
