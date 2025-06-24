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
        raise ValueError("Initial investment must be greater than zero.")

    profit = current_value - initial_investment
    if initial_investment == 0: # This case is already covered by the ValueError, but a secondary check for robustness.
        return 0.0 # Or raise a specific error for initial_investment == 0 if different handling is needed.
    return profit / initial_investment
