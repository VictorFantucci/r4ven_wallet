def calculate_time_to_goal(
    initial_investment, monthly_contribution, monthly_rate, annual_inflation, goal, annual_contribution_adjustment
):
    """
    Calculates the time required to reach an investment goal, considering monthly contributions,
    reinvestment of returns, and annual adjustment of contributions.

    Args:
        initial_investment (float): Initial investment amount.
        monthly_contribution (float): Value of regular monthly contributions.
        monthly_rate (float): Monthly return rate (in decimal, e.g., 0.0077 for 0.77%).
        annual_inflation (float): Annual inflation rate (in decimal, e.g., 0.045 for 4.5%).
        goal (float): Target value to be reached (adjusted for inflation).
        annual_contribution_adjustment (float): Annual adjustment rate for contributions (e.g., 0.05 for a 5% annual increase).

    Returns:
        dict: A dictionary containing the input parameters and the time to the goal in years and months.
    """
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1  # Converts annual inflation to monthly
    balance = initial_investment
    months = 0
    adjusted_goal = goal

    while balance < adjusted_goal:
        # Adjust the monthly contribution with the returns from the balance
        adjusted_monthly_contribution = monthly_contribution + (balance * monthly_rate)
        balance += balance * monthly_rate + adjusted_monthly_contribution  # Update balance with return and contribution
        adjusted_goal *= (1 + monthly_inflation)  # Adjust goal for inflation

        months += 1

        # Every 12 months, adjust the contribution by the annual adjustment rate
        if months % 12 == 0:
            monthly_contribution *= (1 + annual_contribution_adjustment)

    years = months // 12
    remaining_months = months % 12

    result = {
        "initial_investment": initial_investment,
        "monthly_contribution": monthly_contribution,
        "monthly_rate": monthly_rate,
        "annual_inflation": annual_inflation,
        "goal": goal,
        "annual_contribution_adjustment": annual_contribution_adjustment,
        "years": years,
        "months": remaining_months
    }

    return result

def calculate_required_monthly_rate(
    initial_investment, monthly_contribution, annual_inflation, goal, annual_contribution_adjustment, months
):
    """
    Calculates the required monthly return rate to reach an investment goal within a given time frame, 
    considering monthly contributions, reinvestment of returns, and annual adjustment of contributions.

    Parameters:
    initial_investment (float): Initial investment amount.
    monthly_contribution (float): Value of regular monthly contributions.
    annual_inflation (float): Annual inflation rate (in decimal, e.g., 0.045 for 4.5%).
    goal (float): Target value to be reached (adjusted for inflation).
    annual_contribution_adjustment (float): Annual adjustment rate for contributions (e.g., 0.05 for a 5% annual increase).
    months (int): Total time in months to reach the goal.

    Returns:
    dict: A dictionary containing the input parameters and the required monthly rate, with time divided into years and months.
    """
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1  # Converts annual inflation to monthly
    balance = initial_investment
    adjusted_goal = goal

    # Use binary search to find the required monthly rate
    lower_bound, upper_bound = 0.0, 1.0  # Reasonable search range for interest rates (0% to 100% per month)
    tolerance = 1e-6  # Precision for convergence

    while upper_bound - lower_bound > tolerance:
        monthly_rate = (upper_bound + lower_bound) / 2
        temp_balance = initial_investment
        temp_monthly_contribution = monthly_contribution
        temp_adjusted_goal = adjusted_goal

        # Simulate the investment over the given months with the current rate
        for month in range(1, months + 1):
            adjusted_monthly_contribution = temp_monthly_contribution + (temp_balance * monthly_rate)
            temp_balance += temp_balance * monthly_rate + adjusted_monthly_contribution  # Update balance
            temp_adjusted_goal *= (1 + monthly_inflation)  # Adjust goal for inflation

            # Adjust the contribution annually
            if month % 12 == 0:
                temp_monthly_contribution *= (1 + annual_contribution_adjustment)

        # Adjust search range based on result
        if temp_balance < temp_adjusted_goal:
            lower_bound = monthly_rate  # Increase rate
        else:
            upper_bound = monthly_rate  # Decrease rate

    # Final required monthly rate
    required_monthly_rate = (upper_bound + lower_bound) / 2

    years = months // 12
    remaining_months = months % 12

    result = {
        "initial_investment": initial_investment,
        "monthly_contribution": monthly_contribution,
        "annual_inflation": annual_inflation,
        "goal": goal,
        "annual_contribution_adjustment": annual_contribution_adjustment,
        "years": years,
        "months": remaining_months,
        "monthly_rate": required_monthly_rate
    }

    return result