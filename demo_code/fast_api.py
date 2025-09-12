from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import numpy as np

# ----- Define request schema -----
class DataFrameSplit(BaseModel):
    dataframe_split: dict
    model_version_uri: str
    databricks_token: str

# ----- Init FastAPI -----
app = FastAPI(title="MLflow Prediction API")

@app.post("/predict")
def predict(payload: DataFrameSplit):
    """
    Call the deployed MLflow model and compute premiums.
    """
    # Call the deployed MLflow model
    response = requests.post(
        url=payload.model_version_uri,
        headers={"Content-Type": "application/json"},
        auth=("token", payload.databricks_token),
        data=json.dumps({"dataframe_split": payload.dataframe_split})
    )

    # Extract predictions
    frequency_predictions = response.json().get("predictions", [])
    frequency_predictions = np.array(frequency_predictions)

    # Compute severity and burn costs
    severity_prediction = 500
    burn_costs = frequency_predictions * severity_prediction

    # Compute premiums
    margin = 1.2
    premiums = burn_costs * margin 

    return {"premium": premiums.tolist()}
