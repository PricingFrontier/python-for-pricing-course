import polars as pl
import pandas as pd
from typing import  Dict, List, Tuple

def assign_split(data, split):
    """Assigns a split to the data based on the provided split dictionary."""
    field = split.get('field')
    assignment = split.get('assignment')

    data = (
        data
        .with_columns(pl.col(field).replace_strict(assignment, default=None).alias(field))
    )

    return data

def apply_category_mapping(df: pl.DataFrame, category_config: Dict[str, Dict[str, int]]) -> pl.DataFrame:
    """
    Apply category mapping to the DataFrame based on the provided configuration.

    Args:
        df (pl.DataFrame): The input DataFrame.
        category_config (Dict[str, Dict[str, int]]): The category mapping configuration.

    Returns:
        pl.DataFrame: The DataFrame with mapped categories.
    """
    for column, mapping in category_config.items():

        if column not in df.columns:
            continue

        df = df.with_columns(
            pl.col(column).replace_strict(mapping, default = None).cast(pl.Int32).alias(column)
        )

    return df

def continous_to_float(data: pl.DataFrame, columns: List[str]) -> pl.DataFrame:
    """
    Convert specified columns in the DataFrame to float type.

    Args:
        data (pl.DataFrame): The input DataFrame.
        columns (List[str]): List of column names to convert.

    Returns:
        pl.DataFrame: The DataFrame with specified columns converted to float type.
    """
    data = data.with_columns([
        pl.col(col).cast(pl.Float64) for col, dtype in zip(data.select(columns).columns, data.select(columns).dtypes) if dtype == pl.Int64
    ])

    return data


def create_modelling_data(data, features, group_field, group, target, exposure = None) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create modelling data by filtering the DataFrame based on the 'Group' column."
    """
    filtered_data = (
        data
        .filter(pl.col(group_field) == group)
    )

    train_X = (
        filtered_data
        .select(features)
        .to_pandas()
    )

    train_y = (
        filtered_data
        .select(target)
        .to_numpy()
        .ravel()
    )

    if exposure is not None:
        train_exposure = (
            filtered_data
            .with_columns(log_exposure=pl.col(exposure).log())
            .select('log_exposure')
            .to_numpy()
            .ravel()
        )

        return filtered_data, train_X, train_y, train_exposure

    return filtered_data, train_X, train_y

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