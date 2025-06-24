# utils.py

def calculate_net_profit_percentage(initial_investment: float, current_value: float) -> float:
    """
    Calculates the net profit percentage of an investment.

    Args:
        initial_investment: The initial amount invested. Must be greater than 0.
        current_value: The current value of the investment.

    Returns:
        The profit percentage as a float (e.g., 0.10 for 10% profit, -0.05 for 5% loss).

    Raises:
        ValueError: If initial_investment is zero or negative.
    """
    if initial_investment <= 0:
        # It's crucial to raise an error for invalid input, as division by zero
        # or negative investment makes the calculation nonsensical in a real financial context.
        raise ValueError("Initial investment must be greater than zero.")

    profit = current_value - initial_investment
    # No need for a secondary check for initial_investment == 0 here, as the above
    # 'if' condition handles it. The division will be safe if we reach this point.
    return profit / initial_investment
