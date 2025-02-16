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

    def r4ven_bar_plot(self,
                    df: pd.DataFrame,
                    x_data: str,
                    y_value_data: str,
                    y_value_label: str = None,
                    group_method: str = 'sum',
                    title: str = None,
                    tickformat: str = None,
                    orientation: str = 'vertical') -> go.Figure:
        """
        Generate and display a simple bar plot using Plotly with adjustable orientation.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to be plotted.
            x_data (str): The column name in the DataFrame to be used as the x-axis data.
            y_value_data (str): The column name in the DataFrame to be used for the bar heights/values.
            y_value_label (str, optional): The label for the y-axis of the bar plot. Defaults to None.
            group_method (str, optional): The method to aggregate data for bars.
                - 'sum': Aggregates numeric values by summing them (default).
                - 'size': Counts the number of occurrences for each category.
            title (str, optional): The title for the plot. Defaults to None.
            tickformat (str, optional): The tick format to be used in the x-axis labels. Defaults to None.
            orientation (str, optional): The orientation of the bars, 'vertical' or 'horizontal'. Defaults to 'vertical'.

        Returns:
            go.Figure: The Plotly figure containing the bar plot.

        Raises:
            ValueError: If an invalid `group_method` is provided or orientation is not valid.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Validate group_method
            if group_method not in ['sum', 'size']:
                raise ValueError("group_method must be either 'sum' or 'size'.")

            # Validate orientation
            if orientation not in ['vertical', 'horizontal']:
                raise ValueError("orientation must be either 'vertical' or 'horizontal'.")

            # Filter out rows where x_data is None or NaN
            df = df[df[x_data].notna()]

            # Perform grouping based on the chosen method
            if group_method == 'sum':
                grouped_data = df.groupby(x_data)[y_value_data].sum().reset_index()
            else:  # group_method == 'size'
                grouped_data = df.groupby(x_data).size().reset_index(name='counts')

            # Remove any rows where the selected column has 0 values
            grouped_data = grouped_data[grouped_data[y_value_data] > 0]

            # Create the figure for the bar plot
            fig = go.Figure()

            # Define a color palette for the bars
            bar_colors = self.get_dracula_color_palette()

            # Add a single trace for the bar chart
            if orientation == 'vertical':
                fig.add_trace(go.Bar(
                    x=grouped_data[x_data],
                    y=grouped_data[y_value_data],
                    name=y_value_label,
                    marker=dict(color=bar_colors[0]),
                    text=grouped_data[y_value_data].apply(lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)),
                    textposition='auto',
                    opacity=0.7  # Adjust opacity to make the text pop
                ))
            else:  # 'horizontal'
                fig.add_trace(go.Bar(
                    x=grouped_data[y_value_data],
                    y=grouped_data[x_data],
                    name=y_value_label,
                    marker=dict(color=bar_colors[0]),
                    text=grouped_data[y_value_data].apply(lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)),
                    textposition='auto',
                    opacity=0.7
                ))

            # Updating layout to create the bar plot
            fig.update_layout(
                title_text=title,
                barmode='group',  # Group bars for non-stacked visualization
            )

            # Updating axes labels
            if orientation == 'vertical':
                fig.update_yaxes(title_text=y_value_label)
                fig.update_xaxes(
                    tickformat=tickformat  # Optionally format the ticks for date/time
                )
            else:
                fig.update_xaxes(title_text=y_value_label)
                fig.update_yaxes(
                    tickformat=tickformat  # Optionally format the ticks for date/time
                )

            # Return the plot
            return fig

        except Exception as e:
            # Log the exception details and re-raise the exception
            logger.error(f"Data visualization failed: {e}")
            raise
