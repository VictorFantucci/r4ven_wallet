import pandas as pd
from typing import Union, List
import plotly.express as px
import plotly.graph_objects as go
import logging
import traceback
from r4ven_utils.log4me import r4venLogManager

class DataVisualizer:
    def __init__(self, base_log_dir: str):
        """
        Initializes the DataVisualizer instance.

        Args:
            base_log_dir (str): Base directory for storing logs.
        """

        # Initialize logger
        self.log_manager = r4venLogManager(base_log_dir)

    def get_logger(self):
        """ Helper method to get the logger dynamically """
        return self.log_manager.function_logger(__file__, console_level=logging.INFO)

    def get_dracula_color_palette(self):
        """ Helper method to get the Dracula color palette"""
        return [
            "#6272a4",  # Blue
            "#50fa7b",  # Green
            "#f1fa8c",  # Yellow
            "#ff5555",  # Red
            "#8be9fd",  # Cyan
            "#ff79c6",  # Pink
            "#bd93f9",  # Purple
            "#ffb86c",  # Orange
            ]

