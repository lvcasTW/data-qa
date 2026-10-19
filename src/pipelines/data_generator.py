import random
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from src.config import Config, default_config
from src.utils import get_logger, save_dataframe_to_csv

logger = get_logger("data_generator")

class DataGenerator:
    def __init__(self, config: Config = default_config):
        self.config = config

    def generate_sample_data(self, num_records: int = 20) -> Path:
        """
        Generates simulated raw CSV files in the raw landing directory.
        Contains a mix of standard valid records and bad quality records to test the pipelines.
        """
        self.config.ensure_directories()
        
        # Possible categories (including one invalid one: "Vehicles")
        categories = ["Electronics", "Home", "Clothing", "Books", "Sports", "Vehicles"]
        
        records = []
        today = datetime.today()

        # Seed for reproducibility
        random.seed(42)

        for i in range(1, num_records + 1):
            order_id = f"ORD-{1000 + i}"
            customer_id = f"CUST-{random.randint(100, 110)}"
            customer_email = f"user{random.randint(1, 5)}@example.com"
            product_category = random.choice(categories)
            
            # Normal distribution of dates in the last 10 days
            order_date = (today - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d")
            
            quantity = random.randint(1, 5)
            unit_price = round(random.uniform(10.0, 100.0), 2)
            total_amount = round(quantity * unit_price, 2)

            # Introduce intentional quality bugs in some rows
            if i == 3:
                # Issue 1: Negative Price
                unit_price = -15.0
                total_amount = round(quantity * unit_price, 2)
            elif i == 7:
                # Issue 2: Invalid email address
                customer_email = "malformed_email.com"
            elif i == 11:
                # Issue 3: Invalid category (Vehicles is not allowed in ALLOWED_CATEGORIES)
                product_category = "Vehicles"
            elif i == 15:
                # Issue 4: Date in the future
                order_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
            elif i == 18:
                # Issue 5: Math inconsistency (quantity * price != total_amount)
                total_amount = round(quantity * unit_price + 50.0, 2)
            elif i == 20:
                # Issue 6: Empty customer ID
                customer_id = ""

            records.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "customer_email": customer_email,
                "product_category": product_category,
                "order_date": order_date,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": total_amount,
            })

        df = pd.DataFrame(records)
        output_path = self.config.raw_dir / "landing_orders_batch_1.csv"
        save_dataframe_to_csv(df, output_path)
        logger.info(f"Generated {num_records} sample records in raw landing: {output_path}")
        return output_path
