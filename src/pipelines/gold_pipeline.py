import pandas as pd
from datetime import datetime, timezone
from src.config import Config, default_config
from src.utils import get_logger, save_dataframe_to_csv, load_csv_to_dataframe

logger = get_logger("gold_pipeline")

class GoldPipeline:
    def __init__(self, config: Config = default_config):
        self.config = config

    def run(self) -> dict:
        """
        Executes the Gold pipeline.
        Reads validated and clean structured data from SILVER layer,
        aggregates them to generate business metrics/insights,
        and saves them as tables in the GOLD layer.
        
        Returns:
            dict: Metadata about the generated Gold tables.
        """
        logger.info("Starting Gold Aggregation & Business Insights Pipeline...")
        self.config.ensure_directories()

        silver_file = self.config.silver_dir / "orders_silver.csv"
        if not silver_file.exists():
            logger.warning(f"Silver file {silver_file} not found. Skipping Gold pipeline.")
            return {}

        # Load clean Silver data
        df_silver = load_csv_to_dataframe(silver_file)
        if df_silver.empty:
            logger.warning("Silver dataset is empty. Cannot generate Gold metrics.")
            return {}

        # Explicitly parse types for aggregation
        df_silver["quantity"] = df_silver["quantity"].astype(int)
        df_silver["unit_price"] = df_silver["unit_price"].astype(float)
        df_silver["total_amount"] = df_silver["total_amount"].astype(float)
        df_silver["order_date"] = pd.to_datetime(df_silver["order_date"])

        # -------------------------------------------------------------
        # Table 1: Customer Metrics (Customer Profile & Engagement)
        # -------------------------------------------------------------
        logger.info("Generating Gold Table: Customer Metrics...")
        customer_agg = df_silver.groupby("customer_id").agg(
            total_spent=("total_amount", "sum"),
            total_orders=("order_id", "nunique"),
            total_items_bought=("quantity", "sum"),
            last_order_date=("order_date", "max")
        ).reset_index()
        
        customer_agg["average_order_value"] = (customer_agg["total_spent"] / customer_agg["total_orders"]).round(2)
        customer_agg["total_spent"] = customer_agg["total_spent"].round(2)
        customer_agg["last_order_date"] = customer_agg["last_order_date"].dt.strftime("%Y-%m-%d")
        
        # Add metadata column
        customer_agg["_gold_updated_at"] = datetime.now(timezone.utc).isoformat()
        save_dataframe_to_csv(customer_agg, self.config.gold_dir / "customer_metrics.csv")

        # -------------------------------------------------------------
        # Table 2: Category Performance Metrics
        # -------------------------------------------------------------
        logger.info("Generating Gold Table: Product Category Metrics...")
        category_agg = df_silver.groupby("product_category").agg(
            total_revenue=("total_amount", "sum"),
            total_units_sold=("quantity", "sum"),
            order_count=("order_id", "nunique")
        ).reset_index()
        
        category_agg["total_revenue"] = category_agg["total_revenue"].round(2)
        category_agg["average_item_price"] = (category_agg["total_revenue"] / category_agg["total_units_sold"]).round(2)
        category_agg["_gold_updated_at"] = datetime.now(timezone.utc).isoformat()
        save_dataframe_to_csv(category_agg, self.config.gold_dir / "category_metrics.csv")

        # -------------------------------------------------------------
        # Table 3: Daily Sales Trend
        # -------------------------------------------------------------
        logger.info("Generating Gold Table: Daily Sales Metrics...")
        daily_agg = df_silver.groupby("order_date").agg(
            daily_revenue=("total_amount", "sum"),
            daily_orders_count=("order_id", "nunique"),
            daily_items_count=("quantity", "sum")
        ).reset_index()
        
        daily_agg["daily_revenue"] = daily_agg["daily_revenue"].round(2)
        daily_agg["order_date"] = daily_agg["order_date"].dt.strftime("%Y-%m-%d")
        daily_agg = daily_agg.sort_values(by="order_date")
        daily_agg["_gold_updated_at"] = datetime.now(timezone.utc).isoformat()
        save_dataframe_to_csv(daily_agg, self.config.gold_dir / "daily_sales.csv")

        logger.info("Gold pipeline finished successfully. All business metrics tables generated.")
        
        return {
            "customer_metrics_records": len(customer_agg),
            "category_metrics_records": len(category_agg),
            "daily_sales_records": len(daily_agg)
        }
