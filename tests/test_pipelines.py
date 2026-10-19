import pytest
import pandas as pd
from src.config import Config
from src.pipelines.bronze_pipeline import BronzePipeline
from src.pipelines.silver_pipeline import SilverPipeline
from src.pipelines.gold_pipeline import GoldPipeline

def test_full_medallion_pipeline_flow(test_config: Config, sample_raw_dataset):
    """
    Integration test for the entire Medallion pipeline.
    Runs Bronze, Silver, and Gold in sequence against mock data and asserts
    the state and values of each layer.
    """
    # 1. Verify files exist in raw
    raw_files = list(test_config.raw_dir.glob("*.csv"))
    assert len(raw_files) == 1
    assert raw_files[0].name == "test_raw_batch.csv"

    # -------------------------------------------------------------
    # 2. RUN BRONZE PIPELINE
    # -------------------------------------------------------------
    bronze_pipeline = BronzePipeline(test_config)
    bronze_records_count = bronze_pipeline.run()
    
    # Assertions
    assert bronze_records_count == 4
    bronze_file = test_config.bronze_dir / "orders_bronze.csv"
    assert bronze_file.exists()
    
    df_bronze = pd.read_csv(bronze_file)
    assert len(df_bronze) == 4
    assert "_bronze_source_file" in df_bronze.columns
    assert "_bronze_ingested_at" in df_bronze.columns
    assert df_bronze["order_id"].tolist() == ["ORD-101", "ORD-102", "ORD-103", "ORD-104"]

    # -------------------------------------------------------------
    # 3. RUN SILVER PIPELINE (Data Quality Validation & Quarantine)
    # -------------------------------------------------------------
    silver_pipeline = SilverPipeline(test_config)
    silver_metrics = silver_pipeline.run()
    
    # Assertions
    assert silver_metrics["valid_count"] == 2
    assert silver_metrics["quarantined_count"] == 2
    
    silver_file = test_config.silver_dir / "orders_silver.csv"
    quarantine_file = test_config.quarantine_dir / "orders_quarantine.csv"
    
    assert silver_file.exists()
    assert quarantine_file.exists()
    
    df_silver = pd.read_csv(silver_file)
    df_quarantine = pd.read_csv(quarantine_file)
    
    assert len(df_silver) == 2
    assert len(df_quarantine) == 2
    
    # Valid orders: ORD-101, ORD-102
    assert df_silver["order_id"].tolist() == ["ORD-101", "ORD-102"]
    assert "_silver_processed_at" in df_silver.columns
    
    # Quarantined orders: ORD-103 (neg price), ORD-104 (math)
    assert df_quarantine["order_id"].tolist() == ["ORD-103", "ORD-104"]
    assert "quarantine_reason" in df_quarantine.columns
    assert "quarantined_at" in df_quarantine.columns

    # -------------------------------------------------------------
    # 4. RUN GOLD PIPELINE (Aggregations & Analytical Business Views)
    # -------------------------------------------------------------
    gold_pipeline = GoldPipeline(test_config)
    gold_metrics = gold_pipeline.run()
    
    # Assertions
    assert gold_metrics["customer_metrics_records"] == 2
    assert gold_metrics["category_metrics_records"] == 2
    assert gold_metrics["daily_sales_records"] == 2
    
    customer_file = test_config.gold_dir / "customer_metrics.csv"
    category_file = test_config.gold_dir / "category_metrics.csv"
    daily_file = test_config.gold_dir / "daily_sales.csv"
    
    assert customer_file.exists()
    assert category_file.exists()
    assert daily_file.exists()
    
    # Validate Customer Aggregation calculations
    # CUST-01: bought 1 Book at 20.00 -> Spent 20.00, order count 1
    # CUST-02: bought 3 Home items at 15.50 -> Spent 46.50, order count 1
    df_cust = pd.read_csv(customer_file)
    df_cust_sorted = df_cust.sort_values(by="customer_id")
    
    assert df_cust_sorted["customer_id"].tolist() == ["CUST-01", "CUST-02"]
    assert df_cust_sorted["total_spent"].tolist() == [20.00, 46.50]
    assert df_cust_sorted["total_orders"].tolist() == [1, 1]
    assert df_cust_sorted["total_items_bought"].tolist() == [1, 3]
    assert df_cust_sorted["average_order_value"].tolist() == [20.00, 46.50]
    
    # Validate Category Aggregation calculations
    # Books: revenue 20.00
    # Home: revenue 46.50
    df_cat = pd.read_csv(category_file)
    df_cat_sorted = df_cat.sort_values(by="product_category")
    assert df_cat_sorted["product_category"].tolist() == ["Books", "Home"]
    assert df_cat_sorted["total_revenue"].tolist() == [20.00, 46.50]
    assert df_cat_sorted["total_units_sold"].tolist() == [1, 3]
