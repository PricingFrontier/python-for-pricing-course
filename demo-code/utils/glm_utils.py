import h2o
import numpy as np
import polars as pl

def h2o_preprocess(X, y, target, categorical_features, exposure_data = None):
    h2o_df = h2o.H2OFrame(X.to_pandas())

    for categorical_feature in categorical_features:
        h2o_df[categorical_feature]=h2o_df[categorical_feature].asfactor()

    h2o_df[target] = h2o.H2OFrame(y)

    if exposure_data is not None:
        h2o_df['offset'] = h2o.H2OFrame(np.log(exposure_data))

    return h2o_df

def h2o_glm_predictions(data, h2o_data, glm_model):
    
    predictions = glm_model.predict(h2o_data).as_data_frame()
    predictions = predictions['predict'].values

    data = (
        data
        .with_columns(
            pl.Series('glm_predictions', predictions)
        )
    )

    return data