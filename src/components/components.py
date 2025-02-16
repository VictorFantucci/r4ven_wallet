"""
Script that contains streamlit components shared across multiple pages.
"""

# Load packages
import os
import streamlit as st
from PIL import Image

# Load relative packages
from utils import get_src_folder

def set_page_config(page_title: str) -> dict:
    """
    Creates and returns a dictionary with Streamlit page configuration settings.

    Args:
        page_title (str): The title of the page.

    Returns:
        dict: A dictionary containing the page title, page icon, and layout settings.
    """
    # Get the application's source folder path
    app_directory = get_src_folder()

    # Load the page icon from the 'imgs' directory inside 'src'
    page_icon = Image.open(os.path.join(app_directory, 'imgs', 'r4ven_icon.png'))

    # Define the page configuration dictionary
    page_config = {
        'page_title': page_title,  # Set the page title
        'page_icon': page_icon,    # Set the page icon
        'layout': 'wide'           # Set the layout to wide mode
    }

    return page_config
