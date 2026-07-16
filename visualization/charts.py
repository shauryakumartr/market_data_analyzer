"""Module containing chart factory functions for visualization.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Union

logger = logging.getLogger(__name__)

def create_bar_chart(
    data: Union[pd.DataFrame, pd.Series],
    x_label: str,
    y_label: str,
    title: str,
    color_column: Union[str, None] = None,
) -> go.Figure:
    """Create a colored bar chart.

    Parameters
    ----------
    data : pd.Series or pd.DataFrame
        Data to plot.
    x_label, y_label : str
        Axis labels.
    title : str
        Chart title.
    color_column : str or None
        Column to use for coloring bars.

    Returns
    -------
    go.Figure
        Plotly figure.
    """
    logger.info("Creating bar chart: %s", title)
    if isinstance(data, pd.Series):
        fig = px.bar(
            x=data.index,
            y=data.values,
            title=title,
            labels={'x': x_label, 'y': y_label},
            color=data.index,
        )
    else:
        x_col = data.index
        y_col = data.iloc[:, 0] if len(data.columns) == 1 else data[data.columns[0]]
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            labels={'x': x_label, 'y': y_label},
            color=x_col,
        )
    return fig

def create_scatter_chart(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    x_label: str,
    y_label: str,
    size_column: Union[str, None] = None,
    color_column: Union[str, None] = None,
) -> go.Figure:
    """Create a scatter plot.
    """
    logger.info("Creating scatter chart: %s", title)
    fig = px.scatter(
        data,
        x=x_column,
        y=y_column,
        title=title,
        labels={x_column: x_label, y_column: y_label},
        hover_name=data.index,
        size=size_column,
        color=color_column,
    )
    return fig

def create_line_chart(
    data: pd.Series,
    x_label: str,
    y_label: str,
    title: str,
) -> go.Figure:
    """Create a line chart with markers.
    """
    logger.info("Creating line chart: %s", title)
    fig = px.line(
        x=data.index,
        y=data.values,
        title=title,
        labels={'x': x_label, 'y': y_label},
        markers=True,
    )
    return fig

def create_pie_chart(
    data: pd.Series,
    title: str,
    name_label: str = 'Category',
) -> go.Figure:
    """Create a pie chart.
    """
    logger.info("Creating pie chart: %s", title)
    fig = px.pie(
        values=data.values,
        names=data.index,
        title=title,
        labels={'names': name_label},
    )
    return fig
