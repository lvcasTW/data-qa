from datetime import datetime, timezone
import pandas as pd
from pathlib import Path
from src.config import Config, default_config
from src.utils import get_logger, save_dataframe_to_csv, load_csv_to_dataframe

logger = get_logger("bronze_pipeline")

class BronzePipeline:
    def __init__(self, config: Config = default_config):
        self.config = config

    def run(self) -> int:
        """
        Executes the Bronze pipeline.
        Finds all files in the RAW directory, ingests them,
        adds ingestion metadata, and stores them in the BRONZE layer.
        
        Returns:
            int: Number of records processed into Bronze.
        """
        logger.info("Starting Bronze Ingestion Pipeline...")
        self.config.ensure_directories()

        # Find all raw CSV files in raw folder
        raw_files = list(self.config.raw_dir.glob("*.csv"))
        if not raw_files:
            logger.info("No raw files found in raw landing zone directory.")
            return 0

        all_dfs = []
        for file_path in raw_files:
            logger.info(f"Ingesting raw file: {file_path.name}")
            # Read as strings to preserve absolute RAW form (prevent pandas auto-coercion from hiding issues)
            df_raw = pd.read_csv(file_path, dtype=str)
            
            # Add Bronze Ingestion Metadata
            df_raw["_bronze_source_file"] = file_path.name
            df_raw["_bronze_ingested_at"] = datetime.now(timezone.utc).isoformat()
            
            all_dfs.append(df_raw)

        if all_dfs:
            # Combine all ingested raw files
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Save to Bronze folder
            bronze_file = self.config.bronze_dir / "orders_bronze.csv"
            save_dataframe_to_csv(combined_df, bronze_file)
            logger.info(f"Bronze pipeline finished. Successfully ingested {len(combined_df)} records.")
            return len(combined_df)
        
        return 0
