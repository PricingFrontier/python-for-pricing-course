import polars as pl
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import numpy as np
from great_tables import GT, md, html

def band_continuous(
        df, 
        feature, 
        lower_bound, 
        upper_bound, 
        step_size
    ):
    """
    Band the continuous feature into discrete intervals.

    Args:
        df (pl.DataFrame): The input DataFrame.
        feature (str): The name of the continuous feature to be banded.
        lower_bound (float): The lower bound of the feature.
        upper_bound (float): The upper bound of the feature.
        step_size (float): The size of each band.

    Returns:
        pl.DataFrame: The DataFrame with the banded feature.
    """
    banded_data = (
        df
        .with_columns(
            pl.col(feature).clip(lower_bound = lower_bound, upper_bound = upper_bound).alias(feature)
        )
        .with_columns(
            ((pl.col(feature)/step_size).floor()*step_size).alias(feature)
        )
    )    

    return banded_data


def aggregate_frequency_df(
        df, 
        feature, 
        continuous_feature_config, 
        claim_count = 'ClaimCount', 
        exposure = 'Exposure', 
        prediction = 'ClaimCountPrediction'
    ):

    """
    Aggregate frequency data by the specified feature.

    If continuous, bands feature using provided configuration.

    Args:
        df (pl.DataFrame): The input DataFrame.
        feature (str): The name of the feature to aggregate by.
        continuous_feature_config (dict): Configuration for continuous features.
        claim_count (str): The name of the claim count column.
        exposure (str): The name of the exposure column.
        prediction (str): The name of the prediction column.

    Returns:
        pl.DataFrame: The aggregated frequency DataFrame.
    """

    if feature in continuous_feature_config:
        lower_bound = continuous_feature_config.get(feature).get('min')
        upper_bound = continuous_feature_config.get(feature).get('max')
        step_size = continuous_feature_config.get(feature).get('step')

        df = band_continuous(df, feature, lower_bound, upper_bound, step_size)

    aggregated_df = (
        df
        .group_by(feature)
            .agg(
                pl.col(exposure).sum(), 
                pl.col(claim_count).sum(), 
                pl.col(prediction).sum()
            )
        .with_columns(Frequency = pl.col(claim_count) / pl.col(exposure))
        .with_columns(FrequencyPrediction = pl.col(prediction) / pl.col(exposure))
        .sort(feature)
    )

    return aggregated_df


def create_frequency_table(
        df, 
        feature, 
        frequency = 'Frequency', 
        exposure = 'Exposure', 
        prediction = 'FrequencyPrediction', 
        experiment = 'Not Logged'
    ):

    """
    Creates a frequency table for the specified feature.

    Args:
        df (pl.DataFrame): The input DataFrame.
        feature (str): The name of the feature to create a frequency table for.
        frequency (str): The name of the frequency column.
        exposure (str): The name of the exposure column.
        prediction (str): The name of the prediction column.
        experiment (str): The name of the model experiment.

    Returns:
        pl.DataFrame: The created frequency table.
    """
    return (
        GT(df)
        .tab_header(
            title=f'Frequency - Actual vs Predicted - {feature}',
        )
        .tab_stub(rowname_col=feature)
        .tab_source_note(source_note=f'Trained on experiment: {experiment}')
        .tab_stubhead(label=feature)
        .fmt_integer(columns=exposure)
        .fmt_percent(columns=[frequency, prediction], decimals=1)
        .data_color(
            columns=[frequency, prediction],
            palette=["#63BE7B", "#FFEB84", "#F8696B"]
        )
        .cols_move(columns=prediction, after=frequency)
    )

def save_table_to_html(table, path):

    html_str = table.as_raw_html()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_str)

def plot_aggregated_data(visual_data: pl.DataFrame, feature: str, target: str, prediction: str, exposure: str, write_html: bool = False) -> None:

    fig = go.Figure()

    # Bar: Exposure
    fig.add_trace(go.Bar(
        x=visual_data[feature],
        y=visual_data[exposure],
        name=exposure,
        marker_color='lightskyblue',
        yaxis='y1'
    ))

    # Line: ClaimCount
    fig.add_trace(go.Scatter(
        x=visual_data[feature],
        y=visual_data[target],
        name=target,
        mode='lines+markers',
        line=dict(color='firebrick'),
        yaxis='y2'
    ))

    # Line: gbm_predictions
    fig.add_trace(go.Scatter(
        x=visual_data[feature],
        y=visual_data[prediction],
        name="Frequency Predictions",
        mode='lines+markers',
        line=dict(color='green', dash='dot'),
        yaxis='y2'
    ))

    # Layout with dual y-axes
    fig.update_layout(
        title=f"Frequency - Actuals vs Prediction - {feature}",
        xaxis=dict(title=feature),
        yaxis=dict(
            title=exposure,
            side="left",
            showgrid=False
        ),
        yaxis2=dict(
            title="Frequency",
            overlaying="y",
            side="right"
        ),
        barmode='group',
        legend=dict(x=0.01, y=0.99)
    )

    if write_html:
        fig.write_html(f"./frequency-chart-{feature}.html")

    return fig