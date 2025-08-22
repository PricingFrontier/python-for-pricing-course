import polars as pl
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

def agg_glm_vs_gbm(data, factor, continous_features, continous_factor_visuals, target, exposure = None) -> pl.DataFrame:
    """
    Create visual data by filtering the DataFrame based on the 'Group' column."
    """
    visual_data = data

    if exposure is None:
        exposure = 'count'
        visual_data = (
            visual_data
            .with_columns(pl.lit(1).alias(exposure))
        )

    continous_factor_values = continous_factor_visuals.get(factor)

    if continous_factor_values is not None:

        minimum_value = continous_factor_values.get('min')
        maximum_value = continous_factor_values.get('max')
        steps = continous_factor_values.get('step')

        visual_data = (
            visual_data
            .with_columns(
                pl.col(factor).clip(lower_bound = minimum_value, upper_bound = maximum_value).alias(factor)
            )
        )

        visual_data = (
            visual_data
            .with_columns(
                ((pl.col(factor)/steps).round()*steps).alias(factor)
            )
        )

    visual_data = (
        visual_data
        .group_by(factor)
        .agg([
            pl.sum(target).alias(target),
            pl.sum(exposure).alias(exposure),
            pl.sum('gbm_predictions').alias('gbm_predictions'),
            pl.sum('glm_predictions').alias('glm_predictions')
        ])
        .with_columns(
            (pl.col(target) / pl.col(exposure)).alias(target),
            (pl.col('gbm_predictions') / pl.col(exposure)).alias('gbm_predictions'),
            (pl.col('glm_predictions') / pl.col(exposure)).alias('glm_predictions')
        )
    ).sort(factor)

    return visual_data

def plot_glm_vs_gbm(visual_data: pl.DataFrame, factor: str, target: str, exposure: str = None) -> go.Figure:
    if exposure is None:
        exposure = 'count'

    fig = go.Figure()

    # Bar: Exposure
    fig.add_trace(go.Bar(
        x=visual_data[factor],
        y=visual_data[exposure],
        name=exposure,
        marker_color='lightskyblue',
        yaxis='y1'
    ))

    # Line: ClaimCount
    fig.add_trace(go.Scatter(
        x=visual_data[factor],
        y=visual_data[target],
        name=target,
        mode='lines+markers',
        line=dict(color='firebrick'),
        yaxis='y2'
    ))

    # Line: gbm_predictions
    fig.add_trace(go.Scatter(
        x=visual_data[factor],
        y=visual_data["gbm_predictions"],
        name="GBM Predictions",
        mode='lines+markers',
        line=dict(color='green', dash='dot'),
        yaxis='y2'
    ))

    # Line: glm_predictions
    fig.add_trace(go.Scatter(
        x=visual_data[factor],
        y=visual_data["glm_predictions"],
        name="GLM Predictions",
        mode='lines+markers',
        line=dict(color='orange', dash='dash'),
        yaxis='y2'
    ))

    # Layout with dual y-axes
    fig.update_layout(
        title=f"Exposure vs Claims and Predictions by {factor}",
        xaxis=dict(title=factor),
        yaxis=dict(
            title=exposure,
            side="left",
            showgrid=False
        ),
        yaxis2=dict(
            title="severity",
            overlaying="y",
            side="right"
        ),
        barmode='group',
        legend=dict(x=0.01, y=0.99)
    )

    # Layout with dual y-axes
    fig.update_layout(
        title=f"Exposure vs Claims and Predictions by {factor}",
        xaxis=dict(title=factor),
        yaxis=dict(
            title=exposure,
            side="left",
            showgrid=False
        ),
        yaxis2=dict(
            title="severity",
            overlaying="y",
            side="right"
        ),
        barmode='group',
        legend=dict(x=0.01, y=0.99),
        width=1000,
        height=600 
    )
    
    return fig  

def create_html_output(filename, data, continous_features, continous_factor_visuals, target, features, extra_columns = None, exposure = None):
    # Create HTML file with all plots
    features_to_plot = ['gbm_glm_ratio'] + features
    print(f"Processing {len(features_to_plot)} features...")

    # Create list to store all figures
    figures = []

    for i, feature in enumerate(features_to_plot):
        print(f"Processing feature {i+1}/{len(features_to_plot)}: {feature}")
        
        try:
            aggregated_table = create_visual_data(data=data, 
                                                factor=feature, 
                                                continous_features=continous_features, 
                                                continous_factor_visuals=continous_factor_visuals, 
                                                target=target)
            
            fig = plot_glm_vs_gbm(visual_data=aggregated_table, 
                                factor=feature, 
                                target=target)
            
            figures.append(fig)
            print(f"Successfully created plot for {feature}")
            
        except Exception as e:
            print(f"Error processing feature {feature}: {str(e)}")
            continue

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save all plots to a single HTML file
    if figures:
        with open(f'outputs/{filename}_{timestamp}.html', 'w') as f:
            for fig in figures:
                f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        print("HTML file created successfully!.")
    else:
        print("No plots were generated successfully!")





