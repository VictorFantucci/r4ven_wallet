"""
Script that contains streamlit components shared across multiple pages.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS

import os
import pandas as pd
import streamlit as st
from PIL import Image
from typing import List, Union, Dict
from streamlit_option_menu import option_menu

# ------------------------------------------------------------------------------------------------ #
# IMPORTS

# UTILS
from utils import get_src_folder

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
app_directory = get_src_folder()

# ------------------------------------------------------------------------------------------------ #
# CONFIGURATION COMPONENTS
def set_page_config(page_title: str) -> dict:
    """
    Creates and returns a dictionary with Streamlit page configuration settings.

    Args:
        page_title (str): The title of the page.

    Returns:
        dict: A dictionary containing the page title, page icon, and layout settings.
    """

    # Load the page icon from the 'imgs' directory inside 'src'
    page_icon = Image.open(os.path.join(app_directory, 'imgs', 'r4ven_icon.png'))

    # Define the page configuration dictionary
    page_config = {
        'page_title': page_title,  # Set the page title
        'page_icon': page_icon,    # Set the page icon
        'layout': 'wide'           # Set the layout to wide mode
    }

    return page_config

# ------------------------------------------------------------------------------------------------ #
# FILTER COMPONENTS

def get_valid_aggregate_options(df: pd.DataFrame, date_column: str) -> List[str]:
    """
    Determine valid aggregation options based on the data in a date column.

    Args:
        df (pandas.DataFrame): The input DataFrame containing the date column.
        date_column (str): The name of the date column to be analyzed.

    Returns:
        list: A list of valid aggregation options. The options include:
              - 'Day': Included if there are 31 or fewer unique days in the date column.
              - 'Month': Included if there are more than 31 unique days in the date column.
              - 'Quarter': Included if there are 3 or more unique months in the date column.
              - 'Semester': Included if there are 6 or more unique months in the date column.
              - 'Year': Included if there are 12 or more unique months in the date column.
    """

    unique_months = df[date_column].dt.to_period('M').nunique()
    aggregate_options = ['Mês', 'Trimestre', 'Ano']
    valid_options = []

    if unique_months <= 24:
        valid_options.append(aggregate_options[0])
    if unique_months >= 6:
        valid_options.append(aggregate_options[1])
    if unique_months >= 12:
        valid_options.append(aggregate_options[2])
    if unique_months >= 24:
        valid_options.append(aggregate_options[3])

    return valid_options

def aggregate_by_time(df: pd.DataFrame,
                      filter_column: str,
                      target_columns: Union[str, List[str]],
                      time_period: str,
                      agg_functions: Dict[str, List[str]],
                      category_columns: Union[str, List[str], None] = None) -> pd.DataFrame:
    """
    Aggregate data by time period, considering optional categorical columns.

    Args:
        df (pandas DataFrame): The input DataFrame.
        filter_column (str): The column containing timestamps used for filtering.
        target_columns (str or list): The column(s) to aggregate.
        time_period (str): Time period for aggregation - 'day', 'month', 'quarter', or 'year'.
        agg_functions (dict): Dictionary mapping target columns to list of aggregation functions.
        category_columns (str, list, or None): Column(s) for additional grouping.

    Returns:
        pandas DataFrame: Aggregated DataFrame.
    """

    try:
        # Convert filter column to datetime if it's not already
        df[filter_column] = pd.to_datetime(df[filter_column])

        # Define period based on time_period
        period_mapping = {
            'day': 'D', 'd': 'D', 'dia': 'D',
            'month': 'M', 'm': 'M', 'mês': 'M',
            'quarter': 'Q', 'q': 'Q', 'trimestre': 'Q',
            'year': 'Y', 'y': 'Y', 'ano': 'Y'
        }

        time_period = time_period.lower()
        if time_period not in period_mapping:
            raise ValueError("Invalid time period. Choose from 'day', 'month', 'quarter', or 'year'.")

        df['Período'] = df[filter_column].dt.to_period(period_mapping[time_period])

        # Ensure target_columns is a list
        if isinstance(target_columns, str):
            target_columns = [target_columns]

        # Ensure category_columns is a list or None
        if isinstance(category_columns, str):
            category_columns = [category_columns]

        # Define grouping keys (period + any category columns)
        group_by_cols = ['Período'] + (category_columns if category_columns else [])

        # Perform aggregation
        agg_results = df.groupby(group_by_cols).agg({col: agg_functions for col in target_columns})

        # Reset index to bring 'period' and category columns back as normal columns
        agg_results.reset_index(inplace=True)

        # Rename the aggregated columns to reflect both column and function
        new_columns = group_by_cols + [f'{agg} - {col}' for col in target_columns for agg in agg_functions]
        agg_results.columns = new_columns

        # Convert period to string for readability
        agg_results['Período'] = agg_results['Período'].astype(str)

        return agg_results

    except Exception as e:
        raise ValueError(f"Error during aggregation: {e}")

def filter_data_by_time(valid_options: List[str]) -> str:
    """
    Displays a dropdown menu (selectbox) for the user to choose a time period
    for aggregating data.

    Args:
        valid_options (List[str]): A list of valid time periods to display
                                     in the selectbox.

    Returns:
        str: The selected time period from the dropdown menu.
    """

    # Create a selectbox widget in Streamlit for choosing a time period
    filter_by = st.selectbox(
        label='Agregar dados por',  # Label for the dropdown menu
        options=valid_options,  # List of options to choose from
        index=False,  # Set the initial index of the selectbox to False
        help='Períodos pelos quais é possível agregar os dados'  # Tooltip for user guidance
    )

    # Return the selected time period
    return filter_by

# ------------------------------------------------------------------------------------------------ #
# UTILITY COMPONENTS
def reorder_dataframe_columns(df: pd.DataFrame, priority_columns: List[str]) -> pd.DataFrame:

    return df[priority_columns + [col for col in df.columns if col not in priority_columns]]

# ------------------------------------------------------------------------------------------------ #
# WIDGET FUNCTIONS

def set_page_main_menu(selection_dict: dict) -> tuple[str, List[str]]:
    """
    Displays the main menu of the page and returns the user's selection along with the available
    page features.

    This function generates a menu where the user can select from a list of available features.
    It returns the user's selection and the list of all available features.

    Args:
        selection_dict (dict): A dictionary representing the available menu options.
            - Keys represent the names of the page features (options).
            - Values represent the associated icon names (Bootstrap Icons) for each feature.

    Returns:
        tuple:
            - str: The name of the selected page feature (option).
            - List[str]: A list of the names of all available page features (options).
    """

    # Extract the feature names (options) and their corresponding icons from the dictionary
    options = [key for key in selection_dict]
    icons = [value for value in selection_dict.values()]

    # Display the menu with options and icons, set the default index, and define the orientation
    selection = option_menu(None,
                            options=options,
                            icons=icons,
                            menu_icon="cast",
                            default_index=0,
                            orientation="horizontal")

    # Return the selected option and the list of options
    return selection, options
