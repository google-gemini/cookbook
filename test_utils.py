# File: test_utils.py
# To run these tests:
# 1. Make sure you have pytest installed (`pip install pytest`).
# 2. Save the above 'utils.py' and this 'test_utils.py' in the same directory.
# 3. Run `pytest` in your terminal from that directory.

import pytest
from utils import calculate_net_profit_percentage

class TestNetProfitPercentage:
    """
    Comprehensive unit tests for the calculate_net_profit_percentage function.
    Focuses on different scenarios including positive profit, loss, break-even,
    and error handling for invalid inputs.
    """

    def test_positive_profit_simple(self):
        """Test with a simple positive profit scenario."""
        initial = 100.0
        current = 110.0
        expected_profit_percentage = 0.10
        # Using assertAlmostEqual for floating-point comparisons to avoid precision issues
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_positive_profit_larger_numbers(self):
        """Test with larger numbers showing a positive profit."""
        initial = 100000.0
        current = 115000.0
        expected_profit_percentage = 0.15
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_positive_profit_with_decimals(self):
        """Test with floating point numbers for profit calculation."""
        initial = 75.50
        current = 82.00
        expected_profit_percentage = (82.00 - 75.50) / 75.50
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_loss_simple(self):
        """Test with a simple loss scenario."""
        initial = 100.0
        current = 90.0
        expected_profit_percentage = -0.10
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_loss_larger_numbers(self):
        """Test with larger numbers showing a loss."""
        initial = 50000.0
        current = 40000.0
        expected_profit_percentage = -0.20
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_loss_total(self):
        """Test a complete loss scenario where current value is zero."""
        initial = 200.0
        current = 0.0
        expected_profit_percentage = -1.00 # 100% loss
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_break_even(self):
        """Test the break-even scenario where current value equals initial investment."""
        initial = 150.0
        current = 150.0
        expected_profit_percentage = 0.0
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)

    def test_initial_investment_zero_raises_error(self):
        """
        Test that a ValueError is raised when initial_investment is zero.
        Uses pytest.raises to assert that an exception is thrown.
        """
        initial = 0.0
        current = 100.0
        with pytest.raises(ValueError, match="Initial investment must be greater than zero."):
            calculate_net_profit_percentage(initial, current)

    def test_initial_investment_negative_raises_error(self):
        """
        Test that a ValueError is raised when initial_investment is negative.
        """
        initial = -50.0
        current = 100.0
        with pytest.raises(ValueError, match="Initial investment must be greater than zero."):
            calculate_net_profit_percentage(initial, current)

    def test_large_values_accuracy(self):
        """Test with very large floating point numbers for precision."""
        initial = 1_000_000_000.123456
        current = 1_000_000_000.123456 * 1.000000001 # tiny profit
        expected_profit_percentage = 0.000000001
        assert calculate_net_profit_percentage(initial, current) == pytest.approx(expected_profit_percentage)
