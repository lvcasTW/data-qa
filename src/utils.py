import logging
import pandas as pd
from pathlib import Path
from typing import Optional

# Setup high-quality logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def get_logger(name: str) -> logging.Logger:
    """Returns a logger instance with the standard configuration."""
    return logging.getLogger(name)

logger = get_logger("data_lake")

def save_dataframe_to_csv(df: pd.DataFrame, file_path: Path) -> None:
    """
    Saves a Pandas DataFrame to a CSV file.
    Ensures that the directory structure exists beforehand.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)
    logger.info(f"Saved {len(df)} records to {file_path}")

def load_csv_to_dataframe(file_path: Path) -> pd.DataFrame:
    """
    Loads a CSV file into a Pandas DataFrame.
    If the file does not exist, returns an empty DataFrame.
    """
    if not file_path.exists():
        logger.warning(f"File {file_path} does not exist. Returning empty DataFrame.")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} records from {file_path}")
    return df
