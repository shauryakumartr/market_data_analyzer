"""Module containing chart factory functions for visualization.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Union

logger = logging.getLogger(__name__)

# Dark theme layout configuration template for Plotly
DARK_THEME_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8", size=12),
        title=dict(font=dict(size=16, color="#F8FAFC", family="Plus Jakarta Sans, sans-serif")),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.05)",
            zerolinecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.05)",
            zerolinecolor="rgba(255, 255, 255, 0.1)",
            tickfont=dict(color="#94A3B8")
        ),
        margin=dict(l=40, r=40, t=50, b=40)
    )
)

COLOR_DISCRETE_SEQUENCE = ["#6366F1", "#EC4899", "#10B981", "#F59E0B", "#8B5CF6", "#3B82F6"]

def create_bar_chart(
    data: Union[pd.DataFrame, pd.Series],
    x_label: str,
    y_label: str,
    title: str,
    color_column: Union[str, None] = None,
) -> go.Figure:
    """Create a styled colored bar chart.
    """
    logger.info("Creating bar chart: %s", title)
    if isinstance(data, pd.Series):
        fig = px.bar(
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
    fig.update_layout(DARK_THEME_TEMPLATE['layout'], showlegend=False)
    fig.update_traces(marker_line_color='rgba(255,255,255,0.15)', marker_line_width=1, opacity=0.9)
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
    """Create a styled scatter plot.
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
        color_continuous_scale="Viridis" if color_column else None
    )
    fig.update_layout(DARK_THEME_TEMPLATE['layout'])
    fig.update_traces(marker=dict(line=dict(width=1, color='rgba(255,255,255,0.3)')))
    return fig

def create_line_chart(
    data: pd.Series,
    x_label: str,
    y_label: str,
    title: str,
) -> go.Figure:
    """Create a styled line chart with markers.
    """
    logger.info("Creating line chart: %s", title)
    fig = px.line(
        x=data.index,
        y=data.values,
        title=title,
        labels={'x': x_label, 'y': y_label},
        markers=True,
    )
    fig.update_layout(DARK_THEME_TEMPLATE['layout'])
    fig.update_traces(line_color="#EC4899", line_width=3, marker=dict(size=8, color="#6366F1"))
    return fig

def create_pie_chart(
    data: pd.Series,
    title: str,
    name_label: str = 'Category',
) -> go.Figure:
    """Create a styled donut/pie chart.
    """
    logger.info("Creating pie chart: %s", title)
    fig = px.pie(
        values=data.values,
        names=data.index,
        title=title,
        labels={'names': name_label},
        hole=0.4,
        color_discrete_sequence=COLOR_DISCRETE_SEQUENCE
    )
    fig.update_layout(DARK_THEME_TEMPLATE['layout'])
    fig.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#0F172A', width=2)))
    return fig
