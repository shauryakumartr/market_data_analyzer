"""Module containing chart factory functions for executive UI visualization.

Provides styled Plotly visualization builders (Bar Charts, Scatter Plots, Line Charts, Pie/Donut Charts, Funnel Charts)
configured with off-white executive design themes.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Union, Dict, Any, List, Optional

# Module-level logger for visualization chart factories
logger: logging.Logger = logging.getLogger(__name__)

# Light / Off-White executive layout configuration template for Plotly
LIGHT_THEME_TEMPLATE: Dict[str, Any] = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#334155", size=12),
        title=dict(font=dict(size=16, color="#0F172A", family="Plus Jakarta Sans, sans-serif")),
        xaxis=dict(
            gridcolor="#E2E8F0",
            zerolinecolor="#CBD5E1",
            tickfont=dict(color="#475569")
        ),
        yaxis=dict(
            gridcolor="#E2E8F0",
            zerolinecolor="#CBD5E1",
            tickfont=dict(color="#475569")
        ),
        margin=dict(l=40, r=40, t=50, b=40)
    )
)

COLOR_DISCRETE_SEQUENCE: List[str] = ["#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#3B82F6"]


def create_bar_chart(
    data: Union[pd.DataFrame, pd.Series],
    x_label: str,
    y_label: str,
    title: str,
    color_column: Optional[str] = None,
) -> go.Figure:
    """Create a styled colored bar chart.

    Parameters
    ----------
    data : Union[pd.DataFrame, pd.Series]
        Chart input dataset.
    x_label : str
        X-axis title text.
    y_label : str
        Y-axis title text.
    title : str
        Chart header title.
    color_column : Optional[str], optional
        Optional column name for discrete color grouping.

    Returns
    -------
    go.Figure
        Renderable Plotly Figure object.
    """
    logger.info("Creating bar chart figure: '%s'", title)
    if isinstance(data, pd.Series):
        fig: go.Figure = px.bar(
            x=data.index,
            y=data.values,
            title=title,
            labels={'x': x_label, 'y': y_label},
            color=data.index,
            color_discrete_sequence=COLOR_DISCRETE_SEQUENCE
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
            color_discrete_sequence=COLOR_DISCRETE_SEQUENCE
        )
    fig.update_layout(LIGHT_THEME_TEMPLATE['layout'], showlegend=False)
    fig.update_traces(marker_line_color='#CBD5E1', marker_line_width=1, opacity=0.92)
    return fig


def create_scatter_chart(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    x_label: str,
    y_label: str,
    size_column: Optional[str] = None,
    color_column: Optional[str] = None,
) -> go.Figure:
    """Create a styled scatter plot.

    Parameters
    ----------
    data : pd.DataFrame
        Source DataFrame.
    x_column : str
        X-axis dataset column.
    y_column : str
        Y-axis dataset column.
    title : str
        Chart header title.
    x_label : str
        X-axis title text.
    y_label : str
        Y-axis title text.
    size_column : Optional[str], optional
        Column for marker sizing.
    color_column : Optional[str], optional
        Column for color scale mapping.

    Returns
    -------
    go.Figure
        Renderable Plotly Figure object.
    """
    logger.info("Creating scatter chart figure: '%s'", title)
    fig: go.Figure = px.scatter(
        data,
        x=x_column,
        y=y_column,
        title=title,
        labels={x_column: x_label, y_column: y_label},
        hover_name=data.index,
        size=size_column,
        color=color_column,
        color_continuous_scale="Viridis" if color_column else None
    )
    fig.update_layout(LIGHT_THEME_TEMPLATE['layout'])
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='#64748B')))
    return fig


def create_line_chart(
    data: pd.Series,
    x_label: str,
    y_label: str,
    title: str,
) -> go.Figure:
    """Create a styled line chart with markers.

    Parameters
    ----------
    data : pd.Series
        Time series data series.
    x_label : str
        X-axis title text.
    y_label : str
        Y-axis title text.
    title : str
        Chart header title.

    Returns
    -------
    go.Figure
        Renderable Plotly Figure object.
    """
    logger.info("Creating line chart figure: '%s'", title)
    fig: go.Figure = px.line(
        x=data.index,
        y=data.values,
        title=title,
        labels={'x': x_label, 'y': y_label},
        markers=True,
    )
    fig.update_layout(LIGHT_THEME_TEMPLATE['layout'])
    fig.update_traces(line_color="#4F46E5", line_width=3, marker=dict(size=8, color="#06B6D4"))
    return fig


def create_pie_chart(
    data: pd.Series,
    title: str,
    name_label: str = 'Category',
) -> go.Figure:
    """Create a styled donut/pie chart.

    Parameters
    ----------
    data : pd.Series
        Categorical series data.
    title : str
        Chart header title.
    name_label : str, default='Category'
        Label for legend names.

    Returns
    -------
    go.Figure
        Renderable Plotly Figure object.
    """
    logger.info("Creating pie chart figure: '%s'", title)
    fig: go.Figure = px.pie(
        values=data.values,
        names=data.index,
        title=title,
        labels={'names': name_label},
        hole=0.45,
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE
    )
    fig.update_layout(LIGHT_THEME_TEMPLATE['layout'])
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
    return fig


def create_funnel_chart(
    stages_dict: Dict[str, float],
    title: str = "Marketing Funnel Stages Conversion"
) -> go.Figure:
    """Create a styled marketing funnel chart.

    Parameters
    ----------
    stages_dict : Dict[str, float]
        Dictionary mapping stage names to numerical counts.
    title : str, default="Marketing Funnel Stages Conversion"
        Chart header title.

    Returns
    -------
    go.Figure
        Renderable Plotly Figure object.
    """
    logger.info("Creating funnel chart figure: '%s'", title)
    fig: go.Figure = go.Figure(go.Funnel(
        y=list(stages_dict.keys()),
        x=list(stages_dict.values()),
        textinfo="value+percent initial",
        marker=dict(color=["#4F46E5", "#3B82F6", "#06B6D4", "#10B981", "#F59E0B", "#8B5CF6"])
    ))
    fig.update_layout(LIGHT_THEME_TEMPLATE['layout'], title=title)
    return fig
