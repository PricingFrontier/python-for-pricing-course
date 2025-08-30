import json
import polars as pl
from dash import Dash, dcc, html, Input, Output
from utils.visual_utils import aggregate_frequency_df, plot_aggregated_data

# === Load data and config ===
holdout = pl.read_parquet('./demo-code/processed-data/holdout_frequency_predictions.parquet')

with open('./demo-code/config/frequency_config.json', 'r') as f:
    frequency_config = json.load(f)

with open('./demo-code/config/continous_feature_visuals.json', 'r') as f:
    continous_feature_config = json.load(f)

features = frequency_config['features']

# === Dash App ===
app = Dash(__name__)

app.layout = html.Div([
    html.H2("Frequency Chart"),
    
    # Dropdown
    dcc.Dropdown(
        id="feature-dropdown",
        options=[{"label": f, "value": f} for f in features],
        value=features[0],
        clearable=False,
        style={"width": "300px", "margin-bottom": "20px"}
    ),

    # Graph
    dcc.Graph(id="frequency-chart")
])

# === Callback ===
@app.callback(
    Output("frequency-chart", "figure"),
    Input("feature-dropdown", "value"),
)
def update_chart(feature):
    agg_df = aggregate_frequency_df(
        holdout,
        feature=feature,
        continous_feature_config=continous_feature_config
    )
    fig = plot_aggregated_data(
        agg_df,
        feature=feature,
        target="Frequency",
        prediction="FrequencyPrediction",
        exposure="Exposure"
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
