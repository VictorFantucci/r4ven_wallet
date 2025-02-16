"""
Script that contains utility functions used across multiple files of the project.
"""

import os

utils_directory =  os.path.dirname(os.path.dirname(__file__))

def get_src_folder() -> str:
    """
    Returns the path to the source (src) folder.

    Returns:
        str: The absolute path to the src folder.
    """
    return os.path.join(utils_directory, "src")
