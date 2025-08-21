import polars as pl

def gbm_predictions(model, X, data, exposure=None):

    gbm_predictions = model.predict(X)

    if exposure is not None:
        gbm_predictions = gbm_predictions * exposure

    data = (
        data
        .with_columns(
            pl.Series('gbm_predictions', gbm_predictions)
        )
    )

    return data