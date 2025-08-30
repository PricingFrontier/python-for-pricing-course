
import polars as pl
from typing import Optional, Dict, Any, List, Union, Tuple

def define_categorical_columns(data: pl.DataFrame, features: List[str]) -> List[str]:
    """
    Define categorical columns based on the provided features.
    
    Parameters:
    - data: pl.DataFrame
    - features: List[str]
    
    Returns:
    - List[str]: List of categorical column names
    """

    string_columns = [name for name, dtype in zip(data.columns, data.dtypes) if dtype == pl.Utf8]
    categorical_features = [field for field in string_columns if field in features]
    
    return categorical_features

def define_continous_columns(features: List[str], categorical_features: List[str]) -> List[str]:
    """
    Define continuous columns based on the provided features.
    """

    continous_features = [feature for feature in features if feature not in categorical_features]
    
    return continous_features