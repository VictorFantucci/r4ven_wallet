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

    def r4ven_line_plot(self,
                        df: pd.DataFrame,
                        x_data: str,
                        y_data: Union[str, List[str]],
                        dataframe_name: str,
                        ylabel: Union[str, None] = None,
                        title: str = None) -> go.Figure:
        """
        Generate and display a line plot using Plotly Express.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to be plotted.
            x_data (str): The column name in the DataFrame to be used as the x-axis data.
            y_data (Union[str, List[str]]): The column name(s) in the DataFrame to be used as the y-axis data.
                It can be a single column name as a string or a list of column names.
            dataframe_name (str): The name of the DataFrame.
            ylabel (Union[str, None]): The label for the y-axis. If None, the label will not be set.
            title (str): The title for the plot. If None, the title will not be set.

        Returns:
            go.Figure: The Plotly figure containing the line plot.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Define a list of colors for lines
            line_colors = self.get_dracula_color_palette()

            # Creating a line plot with Plotly Express
            fig = px.line(df, x=x_data, y=y_data, title=f'Line Plot of the {dataframe_name}',
                          color_discrete_sequence=line_colors)

            # Updating the traces of the plot to display both lines and markers
            fig.update_traces(mode='lines+markers')

            # Adjust y-axis range to ensure 0 is always visible
            fig.update_yaxes(range=[0, max(df[y_data].max() * 1.1)])  # Adjust multiplier as needed

            # Setting the label for the y-axis if ylabel is provided and y_data is a single string
            if isinstance(y_data, str) and ylabel is not None:
                fig.update_yaxes(title=title)

            # Return the plot
            return fig

        except Exception as e:
            logger.error(f"Data visualization failed: {e}")
            raise
