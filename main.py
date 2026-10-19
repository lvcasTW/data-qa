import sys
from pathlib import Path
from src.config import default_config
from src.pipelines.data_generator import DataGenerator
from src.pipelines.bronze_pipeline import BronzePipeline
from src.pipelines.silver_pipeline import SilverPipeline
from src.pipelines.gold_pipeline import GoldPipeline
from src.utils import get_logger, load_csv_to_dataframe

logger = get_logger("pipeline_orchestrator")

def run_orchestration():
    print("=" * 60)
    print("       MEDALLION DATA PIPELINE ORCHESTRATOR - STARTING      ")
    print("=" * 60)

    # 1. Ensure Directories
    default_config.ensure_directories()

    # 2. Check if raw data exists. If not, generate sample raw data.
    raw_files = list(default_config.raw_dir.glob("*.csv"))
    if not raw_files:
        logger.info("Raw landing zone empty. Initiating mock data generation...")
        generator = DataGenerator(default_config)
        generator.generate_sample_data(num_records=25)
    else:
        logger.info(f"Found {len(raw_files)} existing files in raw landing zone.")

    # 3. Execute Bronze Layer Ingestion
    bronze = BronzePipeline(default_config)
    bronze_count = bronze.run()
    if bronze_count == 0:
        logger.error("Bronze pipeline ingested 0 records. Aborting pipeline run.")
        return

    # 4. Execute Silver Layer Cleaning & Validation
    silver = SilverPipeline(default_config)
    silver_metrics = silver.run()
    
    # 5. Execute Gold Layer Aggregation
    gold = GoldPipeline(default_config)
    gold_metrics = gold.run()

    print("\n" + "=" * 60)
    print("           MEDALLION PIPELINE EXECUTION SUMMARY             ")
    print("=" * 60)
    print(f"Bronze Layer Ingested : {bronze_count} raw records.")
    print(f"Silver Layer Cleaned  : {silver_metrics.get('valid_count', 0)} valid records.")
    print(f"Quarantined Records   : {silver_metrics.get('quarantined_count', 0)} records failed validation.")
    
    if gold_metrics:
        print(f"Gold Tables Created   :")
        print(f"  - Customer Metrics  : {gold_metrics.get('customer_metrics_records', 0)} records")
        print(f"  - Category Metrics  : {gold_metrics.get('category_metrics_records', 0)} records")
        print(f"  - Daily Sales Trends: {gold_metrics.get('daily_sales_records', 0)} records")
    print("=" * 60)

    # If quarantined records exist, show a preview of their reasons for inspection
    quarantine_file = default_config.quarantine_dir / "orders_quarantine.csv"
    if quarantine_file.exists():
        df_q = load_csv_to_dataframe(quarantine_file)
        if not df_q.empty:
            print("\n🚨 DETECTED QUARANTINE ISSUES (DATA QUALITY REPORT) 🚨")
            print("-" * 60)
            for _, row in df_q.iterrows():
                print(f"Order: {row.get('order_id')} | Customer: {row.get('customer_id')} | Field with error:")
                print(f"  └─ Reason: {row.get('quarantine_reason')}")
            print("-" * 60)
    
    print("\nData pipeline completed! You can explore the 'data/' folder to inspect the physical files.")
    print("=" * 60)

if __name__ == "__main__":
    run_orchestration()
