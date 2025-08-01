"""
Script that contains utility functions used across multiple files of the project.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime

utils_directory =  os.path.dirname(os.path.dirname(__file__))

def get_src_folder() -> str:
    """
    Returns the path to the source (src) folder.

    Returns:
        str: The absolute path to the src folder.
    """
    return os.path.join(utils_directory, "src")

def list_financial_goals() -> list:
    """
    Returns a list of predefined financial goal options.

    Each goal is represented as a tuple containing:
        - an integer value of the financial goal in Brazilian Reais (BRL),
        - a formatted string representation with currency symbol and thousand separators.

    Returns:
        list: A list of tuples, each representing a financial goal.
              Example: [(25000, 'R$ 25,000'), (50000, 'R$ 50,000'), ...]
    """
    return [
        (25000, 'R$ 25,000'),
        (50000, 'R$ 50,000'),
        (75000, 'R$ 75,000'),
        (100000, 'R$ 100,000'),
        (250000, 'R$ 250,000'),
        (500000, 'R$ 500,000'),
        (750000, 'R$ 750,000'),
        (1000000, 'R$ 1,000,000'),
        (2500000, 'R$ 2,500,000'),
        (5000000, 'R$ 5,000,000'),
        (7500000, 'R$ 7,500,000'),
        (10000000, 'R$ 10,000,000')
    ]

def financial_goals_achieved(start_date: str) -> pd.DataFrame:
    """
    Generates a DataFrame containing each financial goal, the date it was achieved,
    and the number of months from the start date to the achievement date.

    If there are more goals than dates, missing dates are filled with NaN.

    Args:
        start_date (str): The start date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: A DataFrame with columns: 'goal', 'label', 'achieved_date', 'months_from_start'.
    """

    # Dates of goal achievement (in chronological order)
    achieved_dates = [
        '2025-05-31',
        # Fewer dates than goals; remaining will be np.nan
    ]

    goals = list_financial_goals()
    goal_values = [g[0] for g in goals]
    goal_labels = [g[1] for g in goals]

    # Pad dates with np.nan if fewer than goals
    achieved_dates += [np.nan] * (len(goals) - len(achieved_dates))

    # Calculate months from start
    start = datetime.strptime(start_date, '%Y-%m-%d')
    months_from_start = []
    for date in achieved_dates:
        if pd.isna(date):
            months_from_start.append(np.nan)
        else:
            d = datetime.strptime(date, '%Y-%m-%d')
            delta = (d.year - start.year) * 12 + (d.month - start.month)
            months_from_start.append(delta)

    # Create DataFrame
    df = pd.DataFrame({
        'Meta': goal_labels,
        'Data da Conquista': achieved_dates,
        'Tempo em Meses': months_from_start
    })

    return df.dropna(subset=['Data da Conquista'])
