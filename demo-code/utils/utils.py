
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


def convert_notebook(notebook_path: str, output_format: str = 'html') -> None:
    """
    Convert a Jupyter notebook to specified format with date in filename.
    
    Parameters:
    -----------
    notebook_path : str
        Path to the notebook file
    output_format : str
        Format to convert to ('html', 'pdf', 'python')
    """
    import subprocess
    import os
    from datetime import datetime

    # Validate format
    valid_formats = ['html', 'pdf', 'python']
    if output_format not in valid_formats:
        raise ValueError(f"Format must be one of {valid_formats}")
    
    # Get current timestamp for unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get directory path and base filename
    dir_path = os.path.dirname(notebook_path)
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    
    # Create new filename with timestamp
    output_name = f"{base_name}_{timestamp}"
    
    try:
        # Run nbconvert with specific output path
        cmd = [
            'jupyter',
            'nbconvert',
            '--to', output_format,
            '--output', output_name,
            notebook_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        output_file = f"{output_name}.{output_format}"
        if result.returncode == 0:
            print(f"Successfully converted notebook to: {output_file}")
        else:
            print(f"Error converting notebook: {result.stderr}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# To use the function, run:
# convert_notebook('GLM_v_GBM_severity.ipynb', 'html')