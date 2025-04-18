"""
Script that contains class with plotly visualization used across multiple pages of the project.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS
import streamlit as st
import pandas as pd
from typing import Union, List
import plotly.express as px
import plotly.graph_objects as go
import logging
from r4ven_utils.log4me import r4venLogManager

# ------------------------------------------------------------------------------------------------ #
# RELATIVE IMPORTS

# UTILS
from utils import get_src_folder

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
logs_folder = get_src_folder()

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

    def get_r4ven_color_palette(self):
        """Helper method to get the Sweetie 16 color palette."""
        return [
            "#A7F070",  # Fresh Green
            "#5D275D",  # Rich Purple
            "#FFCD75",  # Soft Gold
            "#EF7D57",  # Warm Coral
            "#B13E53",  # Deep Red
            "#38B764",  # Vibrant Teal Green
            "#FF79C6",  # Pink
            "#8BE9FD",  # Cyan
            "#73EFF7",  # Soft Cyan
            "#41A6F6",  # Sky Blue
            "#3B5DC9",  # Bright Blue
            "#257179",  # Deep Cyan
            "#29366F",  # Dark Indigo
            "#94B0C2",  # Muted Blue-Gray
            "#F4F4F4",  # Light Gray-White
            "#333C57",  # Charcoal Blue
        ]

    def r4ven_line_plot(self,
                        df: pd.DataFrame,
                        x_data: str,
                        y_data: Union[str, List[str]],
                        title: str = None,
                        tickformat: str = None) -> go.Figure:
        """
        Generate and display a line plot using Plotly Express.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to be plotted.
            x_data (str): The column name in the DataFrame to be used as the x-axis data.
            y_data (Union[str, List[str]]): The column name(s) in the DataFrame to be used as the y-axis data.
                It can be a single column name as a string or a list of column names.
            title (str): The title for the plot. If None, the title will not be set.
            tickformat (str, optional): The tick format to be used in the x-axis labels. Defaults to None.

        Returns:
            go.Figure: The Plotly figure containing the line plot.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Define a list of colors for lines
            line_colors = self.get_r4ven_color_palette()

            # Creating a line plot with Plotly Express
            fig = px.line(df, x=x_data, y=y_data, title=title,
                          color_discrete_sequence=line_colors)

            # Updating the traces of the plot to display both lines and markers
            fig.update_traces(mode='lines+markers')

            # Optionally format the ticks for date/time

            fig.update_xaxes(
                tickformat=tickformat,
                tickvals=df[x_data].unique(),
                tickangle=45
            )

            # Adjust y-axis range to ensure 0 is always visible
            y_max = df[y_data].max() * 1.1
            y_max = y_max.max() if isinstance(y_max, pd.Series) else y_max
            fig.update_yaxes(range=[0, y_max])

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
                        tickformat: str = None) -> go.Figure:
        """
        Generate and display a simple vertical bar plot using Plotly.

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

        Returns:
            go.Figure: The Plotly figure containing the bar plot.

        Raises:
            ValueError: If an invalid `group_method` is provided.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Validate group_method
            if group_method not in ['sum', 'size']:
                raise ValueError("group_method must be either 'sum' or 'size'.")

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
            bar_colors = self.get_r4ven_color_palette()

            # Add a single trace for the bar chart
            fig.add_trace(go.Bar(
                x=grouped_data[x_data],
                y=grouped_data[y_value_data],
                name=y_value_label,
                marker=dict(color=bar_colors[0]),
                text=grouped_data[y_value_data].apply(lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)),
                textposition='auto',
                opacity=0.7  # Adjust opacity to make the text pop
            ))

            # Updating layout to create the bar plot
            fig.update_layout(
                title_text=title,
                barmode='group'  # Group bars for non-stacked visualization
            )

            # Updating axes labels
            fig.update_yaxes(title_text=y_value_label)
            fig.update_xaxes(
                tickformat=tickformat,
                tickvals=df[x_data].unique(),
                tickangle=45
            )

            # Return the plot
            return fig

        except Exception as e:
            # Log the exception details and re-raise the exception
            logger.error(f"Data visualization failed: {e}")
            raise

    def r4ven_stacked_bar_plot(self,
                            df: pd.DataFrame,
                            x_data: str,
                            y_stack_data: str,
                            y_stack_label: str = None,
                            group_method: str = 'sum',
                            title: str = None,
                            tickformat: str = None) -> go.Figure:
        """
        Generate and display a stacked bar plot using Plotly.

        Args:
            df (pd.DataFrame): The DataFrame containing the data to be plotted.
            x_data (str): The column name in the DataFrame to be used as the x-axis data.
            y_stack_data (str): The column name in the DataFrame to be used for stacking.
            y_stack_label (str, optional): The label for the y-axis of the stacked bar plot. Defaults to None.
            group_method (str, optional): The method to aggregate data for stacking.
                - 'sum': Aggregates numeric values by summing them (default).
                - 'size': Counts the number of occurrences for each category.
            title (str, optional): The title for the plot. Defaults to None.
            tickformat (str, optional): The tick format to be used in the x-axis labels. Defaults to None.

        Returns:
            go.Figure: The Plotly figure containing the stacked bar plot.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Validate group_method
            if group_method not in ['sum', 'size']:
                raise ValueError("group_method must be either 'sum' or 'size'.")

            # Filter out rows where x_data is None or NaN
            df = df[df[x_data].notna()]

            # Perform grouping based on the chosen method
            if group_method == 'sum':
                grouped_data = df.groupby([x_data, y_stack_data])[y_stack_label].sum().reset_index()
            else:  # group_method == 'size'
                grouped_data = df.groupby([x_data, y_stack_data]).size().reset_index(name='counts')

            # Determine the correct column to pivot on
            value_column = 'counts' if group_method == 'size' else y_stack_label

            # Remove any rows where the selected column has 0 values
            grouped_data = grouped_data[grouped_data[value_column] > 0]

            # Create a pivot table where rows are x_data and columns are y_stack_data categories
            pivot_data = grouped_data.pivot(index=x_data, columns=y_stack_data, values=value_column).fillna(0)

            # Drop rows where all values are 0.0
            pivot_data = pivot_data[(pivot_data != 0).any(axis=1)]

            # Create the figure for the stacked bar plot
            fig = go.Figure()

            # Define a list of colors for the stacked bars
            stack_colors = self.get_r4ven_color_palette()[1:]

            # Replace x_data with a numeric index for plotting
            x_numeric = list(range(len(pivot_data.index)))

            # Add traces for each category in y_stack_data to create the stacked bars
            for i, column in enumerate(pivot_data.columns):
                fig.add_trace(go.Bar(
                    x=x_numeric,
                    y=pivot_data[column],
                    name=column,
                    marker=dict(color=stack_colors[i % len(stack_colors)]),
                    text=pivot_data[column].apply(lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)),
                    textposition='auto',  # Adjust text position for readability
                    opacity=0.7  # Adjust opacity to make the text pop
                ))

            # Updating layout to create the stacked bar plot
            fig.update_layout(title_text=title,
                              barmode='stack',
                            )

            # Updating y-axis label
            fig.update_yaxes(title_text=y_stack_label)

            # Update x-axis to use numeric indices but show actual date labels
            fig.update_xaxes(
                tickmode='array',  # Use 'array' mode for custom tick values
                tickvals=x_numeric,  # Position of each tick corresponds to numeric index
                ticktext=pivot_data.index.astype(str),  # Display date labels from the index
                tickangle=45,  # Rotate labels for better readability
                tickfont=dict(size=10),
                tickformat=tickformat  # Optionally format the ticks for date/time
            )

            # Return the plot
            return fig

        except Exception as e:
            # Log the exception details and re-raise the exception
            logger.error(f"Data visualization failed: {e}")
            raise

    def r4ven_gauge_plot(self,
                         total_value: float,
                         actual_value: float,
                         title: str = "Gauge Chart") -> go.Figure:
        """
        Generate and display a gauge chart using Plotly.

        Args:
            total_value (float): The maximum value of the gauge.
            actual_value (float): The current value to be displayed on the gauge.
            title (str): The title for the gauge chart.

        Returns:
            go.Figure: The Plotly figure containing the gauge chart.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Ensure actual_value does not exceed total_value
            actual_value = min(actual_value, total_value)

            # Creating a gauge chart with Plotly
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=actual_value,
                title={'text': title},
                gauge={
                    'axis': {'range': [0, total_value]},
                    'bar': {'color': self.get_r4ven_color_palette()[-2]}
                    }
                )
            )

            return fig

        except Exception as e:
            logger.error(f"Gauge visualization failed: {e}")
            raise

    def r4ven_pie_plot(self,
                       df: pd.DataFrame,
                       value_column: str,
                       label_column: str,
                       title: str = "Pie Chart") -> go.Figure:
        """
        Generate and display a pie chart using Plotly from a DataFrame.

        Args:
            df (pandas.DataFrame): The DataFrame containing the data.
            value_column (str): The name of the column with values for the pie chart.
            label_column (str): The name of the column with labels for the pie chart.
            title (str): The title for the pie chart.

        Returns:
            go.Figure: The Plotly figure containing the pie chart.
        """

        # Create a logger object for this function
        logger = self.get_logger()

        try:
            # Ensure the specified columns exist in the DataFrame
            if value_column not in df.columns or label_column not in df.columns:
                raise ValueError(f"Columns '{value_column}' or '{label_column}' not found in the DataFrame.")

            # Extract values and labels from the DataFrame
            values = df[value_column].tolist()
            labels = df[label_column].tolist()

            # Creating a pie chart with Plotly
            fig = go.Figure(go.Pie(
                values=values,
                labels=labels,
                title={'text': title},
                marker=dict(
                    colors=self.get_r4ven_color_palette()[:len(values)]  # Adjusting color palette based on number of slices
                ),
                opacity=0.7
            ))

            return fig

        except Exception as e:
            logger.error(f"Pie chart visualization failed: {e}")
            raise

# ------------------------------------------------------------------------------------------------ #
# VIZ FUNCTIONS

def show_stacked_bar_chart(df: pd.DataFrame,
                                  x_data: str,
                                  y_stack_data: str,
                                  y_stack_label: str,
                                  title: str,
                                  tickformat: str = None):
    """
    Display a stacked bar chart for income data.

    Args:
        df (DataFrame): The input data frame containing income details.
        x_data (str): The column name representing the x-axis.
        y_stack_data (str): The column name representing the stacked categories.
        y_stack_label (str): The column name representing the values to be summed.
        title (str): The title of the chart.
        tickformat (str): The format for the x-axis ticks.
            Defaults to None, to auto-format the x-axis.

    Returns:
        None: Displays the generated stacked bar chart.
    """

    # Agrupar por x_col e y_stack_data
    income_by_type = df.groupby([x_data, y_stack_data])[y_stack_label].sum().reset_index()

    viz = DataVisualizer(logs_folder)

    # Generate the stacked bar plot
    fig = viz.r4ven_stacked_bar_plot(
        df=income_by_type,
        x_data=x_data,
        y_stack_data=y_stack_data,
        y_stack_label=y_stack_label,
        title=title,
        tickformat=tickformat
    )

    st.plotly_chart(fig, use_container_width=True)

def show_bar_chart(df: pd.DataFrame,
                   x_data: str,
                   y_value_data: str,
                   y_value_label: str,
                   title: str,
                   tickformat: str = None):
    """
    Display a bar chart for accumulated income data.

    Args:
        df (DataFrame): The input data frame containing income details.
        x_data (str): The column name representing the x-axis.
        y_value_data(str): The column name representing the s.
        y_value_label (str): The column name representing the values to be summed.
        title (str): The title of the chart.
        tickformat (str): The format for the x-axis ticks.
            Defaults to None, to auto-format the x-axis.

    Returns:
        None: Displays the generated stacked bar chart.
    """
    # Ensure DataFrame is sorted by x_data
    df_sorted = df.sort_values(by=x_data)

    # Group by x_data and sum values
    df_grouped = df_sorted.groupby(x_data)[y_value_data].sum().reset_index()

    logs_folder = get_src_folder()
    viz = DataVisualizer(logs_folder)

    # Plot the accumulated values
    fig = viz.r4ven_bar_plot(
        df=df_grouped,
        x_data=x_data,
        y_value_data=y_value_data,
        y_value_label=y_value_label,
        title=title,
        tickformat=tickformat
    )

    st.plotly_chart(fig, use_container_width=True)

def show_line_chart(df: pd.DataFrame,
                    x_data: str,
                    y_data: str,
                    title: str,
                    tickformat: str = None):
    """
    Display a bar chart for accumulated income data.

    Args:
        df (DataFrame): The input data frame containing income details.
        x_data (str): The column name representing the x-axis.
        y_data(str): The column name representing the y-axis.
        title (str): The title of the chart.
        tickformat (str): The format for the x-axis ticks.
            Defaults to None, to auto-format the x-axis.

    Returns:
        None: Displays the generated stacked bar chart.
    """
    # Ensure DataFrame is sorted by x_data
    df_sorted = df.sort_values(by=x_data)

    logs_folder = get_src_folder()
    viz = DataVisualizer(logs_folder)

    # Plot the accumulated values
    fig = viz.r4ven_line_plot(
        df=df_sorted,
        x_data=x_data,
        y_data=y_data,
        title=title,
        tickformat=tickformat
    )

    st.plotly_chart(fig, use_container_width=True)

def show_accumulated_bar_chart(df: pd.DataFrame,
                               x_data: str,
                               y_value_data: str,
                               y_value_label: str,
                               title: str,
                               tickformat: str = None):
    """
    Display a bar chart for accumulated income data.

    Args:
        df (DataFrame): The input data frame containing income details.
        x_data (str): The column name representing the x-axis.
        y_value_data(str): The column name representing the s.
        y_value_label (str): The column name representing the values to be summed.
        title (str): The title of the chart.
        tickformat (str): The format for the x-axis ticks.
            Defaults to None, to auto-format the x-axis.

    Returns:
        None: Displays the generated stacked bar chart.
    """
    # Ensure DataFrame is sorted by x_data
    df_sorted = df.sort_values(by=x_data)

    # Group by x_data and sum values
    df_grouped = df_sorted.groupby(x_data)[y_value_data].sum().reset_index()

    # Compute cumulative sum
    df_grouped["Valor Acumulado"] = df_grouped[y_value_data].cumsum()

    logs_folder = get_src_folder()
    viz = DataVisualizer(logs_folder)

    # Plot the accumulated values
    fig = viz.r4ven_bar_plot(
        df=df_grouped,
        x_data=x_data,
        y_value_data="Valor Acumulado",
        y_value_label=y_value_label,
        title=title,
        tickformat=tickformat
    )

    st.plotly_chart(fig, use_container_width=True)

def show_pie_plot(df: pd.DataFrame,
                  value_column: str,
                  label_column: str,
                  title: str):
    """_summary_

    Args:
        df (pd.DataFrame): _description_
        value_column (str): _description_
        label_column (str): _description_
        title (str): _description_
    """

    logs_folder = get_src_folder()
    viz = DataVisualizer(logs_folder)

    # Plot pie plot
    fig = viz.r4ven_pie_plot(
        df=df,
        value_column=value_column,
        label_column=label_column,
        title=title
    )

    st.plotly_chart(fig, use_container_width=True)
