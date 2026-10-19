import pandas as pd
from datetime import datetime, timezone
from src.config import Config, default_config
from src.utils import get_logger, save_dataframe_to_csv, load_csv_to_dataframe
from src.validation.schemas import validate_records

logger = get_logger("silver_pipeline")

class SilverPipeline:
    def __init__(self, config: Config = default_config):
        self.config = config

    def run(self) -> dict:
        """
        Executes the Silver pipeline.
        Reads raw data from BRONZE, cleanses and validates records,
        splits them into clean (Silver) and quarantined data (Quarantine).
        
        Returns:
            dict: Summary metrics containing count of valid and quarantined records.
        """
        logger.info("Starting Silver Cleaning & Quality Validation Pipeline...")
        self.config.ensure_directories()

        bronze_file = self.config.bronze_dir / "orders_bronze.csv"
        if not bronze_file.exists():
            logger.warning(f"Bronze file {bronze_file} not found. Skipping Silver pipeline.")
            return {"valid_count": 0, "quarantined_count": 0}

        # Load bronze data
        df_bronze = load_csv_to_dataframe(bronze_file)
        if df_bronze.empty:
            logger.warning("Bronze dataset is empty.")
            return {"valid_count": 0, "quarantined_count": 0}

        # Remove pandas-specific NaN issues by converting to Python None, allowing Pydantic validation
        # pd.DataFrame.to_dict(orient='records') converts NaNs to float('nan'). We replace nan with None.
        raw_records = df_bronze.to_dict(orient="records")
        clean_raw_records = []
        for rec in raw_records:
            cleaned_rec = {}
            for k, v in rec.items():
                # Filter out Pandas NaN values
                if pd.isna(v):
                    cleaned_rec[k] = None
                else:
                    cleaned_rec[k] = v
            clean_raw_records.append(cleaned_rec)

        # Run Data Quality validation!
        valid_records, quarantined_records = validate_records(clean_raw_records)

        # Process and save Valid (Silver) data
        if valid_records:
            df_silver = pd.DataFrame(valid_records)
            # Add Silver processing metadata
            df_silver["_silver_processed_at"] = datetime.now(timezone.utc).isoformat()
            
            silver_file = self.config.silver_dir / "orders_silver.csv"
            save_dataframe_to_csv(df_silver, silver_file)
        else:
            logger.info("No valid records found for Silver layer.")
            # If there's an empty or outdated silver file, we might want to clear it or write empty df
            df_silver = pd.DataFrame()

        # Process and save Quarantined data
        if quarantined_records:
            df_quarantine = pd.DataFrame(quarantined_records)
            quarantine_file = self.config.quarantine_dir / "orders_quarantine.csv"
            save_dataframe_to_csv(df_quarantine, quarantine_file)
            logger.warning(f"Quarantined {len(quarantined_records)} records due to validation failures!")
        else:
            logger.info("Awesome! Zero records were quarantined.")

        metrics = {
            "valid_count": len(valid_records),
            "quarantined_count": len(quarantined_records)
        }
        
        logger.info(f"Silver pipeline finished. Valid: {metrics['valid_count']} | Quarantined: {metrics['quarantined_count']}")
        return metrics
