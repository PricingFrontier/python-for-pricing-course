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

    # Call the deployed MLflow model
    response = requests.post(
        payload.model_version_uri,
        headers={"Content-Type": "application/json"},
        auth=("token", payload.databricks_token),
        data=json.dumps({"dataframe_split": payload.dataframe_split})
    )

    frequency_predictions = response.json().get("predictions")
    frequency_predictions = np.array(frequency_predictions)

    severity_prediction = 500
    burn_costs = frequency_predictions * severity_prediction
    premiums = burn_costs * 1.2

    return {"premium": premiums.tolist()}
