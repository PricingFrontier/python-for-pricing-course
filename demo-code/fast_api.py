from fastapi import FastAPI
from pydantic import BaseModel
import mlflow.pyfunc
import numpy as np
from dotenv import load_dotenv
import os

# Load variables from .env into os.environ
load_dotenv()

# Access them like normal environment variables
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

os.environ["DATABRICKS_HOST"] = DATABRICKS_HOST
os.environ["DATABRICKS_TOKEN"] = DATABRICKS_TOKEN
os.environ["MLFLOW_ENABLE_UC_FUNCTIONS"] = "true"

model = mlflow.pyfunc.load_model("models:/workspace.default.models.frequency_gbm@champion")
FEATURES = [col.name for col in model.metadata.get_input_schema().inputs]

# Dynamically build Pydantic model
InputSchema = type(
    "InputSchema",
    (BaseModel,),
    {f: (float, ...) for f in FEATURES}  # ... means required
)

app = FastAPI()

@app.post("/predict")
def predict(data: InputSchema):
    x = np.array([[getattr(data, f) for f in FEATURES]], dtype=np.float32)
    pred = model.predict(x)
    return {"prediction": pred.tolist()}
