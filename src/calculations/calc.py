"""
Script that contains calculations for the application simulation.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS

import pandas as pd
from datetime import datetime
from scipy.optimize import fsolve

# ------------------------------------------------------------------------------------------------ #
# SIMULATIONS

def calculate_time_to_goal(initial_investment: float,
                           monthly_contribution: float,
                           monthly_rate: float,
                           annual_inflation: float,
                           goal: float,
                           annual_contribution_adjustment: float,
                           start_year_month: str) -> dict:
    """
    Calculates the time required to reach an investment goal, considering monthly contributions,
    reinvestment of returns, and annual adjustment of contributions. Also returns a DataFrame
    detailing the investment progress.

    Args:
        initial_investment (float): Initial investment amount.
        monthly_contribution (float): Value of regular monthly contributions.
        monthly_rate (float): Monthly return rate (in decimal, e.g., 0.0077 for 0.77%).
        annual_inflation (float): Annual inflation rate (in decimal, e.g., 0.045 for 4.5%).
        goal (float): Target value to be reached (adjusted for inflation).
        annual_contribution_adjustment (float): Annual adjustment rate for contributions (e.g., 0.05 for a 5% annual increase).
        start_year_month (str): Initial year and month in format 'YYYY-MM'.

    Returns:
        dict: A dictionary containing the input parameters, the time to the goal in years and months,
              and a DataFrame with investment progress details.
    """
    monthly_inflation = (1 + annual_inflation) ** (1 / 12) - 1  # Converts annual inflation to monthly
    balance = initial_investment
    months = 0
    adjusted_goal = goal

    # Extract year and month from start_year_month
    start_year, start_month = map(int, start_year_month.split('-'))
    current_date = datetime(start_year, start_month, 1)
    start_date = current_date 

    data = []  # List to store DataFrame data
    total_return_last_month = 0

    while balance < adjusted_goal:
        # Adjust the monthly contribution with the returns from the balance
        adjusted_monthly_contribution = monthly_contribution + total_return_last_month
        total_return = balance * monthly_rate
        balance += total_return + adjusted_monthly_contribution  # Update balance with return and contribution
        adjusted_goal *= (1 + monthly_inflation)  # Adjust goal for inflation

        # Store data for DataFrame
        data.append({
            "Mês": pd.Period(year=current_date.year, month=current_date.month, freq='M'),
            "Aporte": round(adjusted_monthly_contribution, 2),
            "Patrimônio (R$)": round(balance, 2),
            "Proventos (R$)": round(total_return, 2),
            "Retorno Mensal (%)": round(monthly_rate * 100, 2)
        })

        months += 1
        # Increment the current month by one
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

        total_return_last_month = total_return  # Update total return for next month's contribution

        # Every 12 months, adjust the contribution by the annual adjustment rate
        if months % 12 == 0:
            monthly_contribution *= (1 + annual_contribution_adjustment)

    years = months // 12
    remaining_months = months % 12
    df = pd.DataFrame(data)

    # Calculate the expected year-month when the goal is reached
    if start_date.month + remaining_months <= 12:
        expected_year_month = (start_date.replace(year=start_date.year + years,
                                                    month=start_date.month + remaining_months)
                            .strftime('%Y-%m'))
    else:
        fix_remaining_months = (start_date.month + remaining_months) - 12
        expected_year_month = (start_date.replace(year=start_date.year + years + 1,
                                                    month=fix_remaining_months)
                            .strftime('%Y-%m'))

    result = {
        "initial_investment": initial_investment,
        "monthly_contribution": monthly_contribution,
        "monthly_rate": monthly_rate,
        "annual_inflation": annual_inflation,
        "goal": goal,
        "adjusted_goal": adjusted_goal,
        "annual_contribution_adjustment": annual_contribution_adjustment,
        "years": years,
        "months": remaining_months,
        "dataframe": df,
        "expected_year_month": expected_year_month
    }

    return result
