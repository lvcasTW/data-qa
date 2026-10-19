import pytest
from pathlib import Path
import pandas as pd
from src.config import Config

@pytest.fixture
def test_config(tmp_path: Path) -> Config:
    """
    Fixture that provides an isolated Config instance pointing to a temporary directory.
    This guarantees that tests do not write into or read from the main 'data/' directory.
    """
    config = Config(data_root=tmp_path / "test_data_lake")
    config.ensure_directories()
    return config

@pytest.fixture
def sample_valid_order_dict() -> dict:
    """Provides a single valid raw order dict."""
    return {
        "order_id": "ORD-1234",
        "customer_id": "CUST-999",
        "customer_email": "test@example.com",
        "product_category": "Electronics",
        "order_date": "2026-09-20",
        "quantity": "2",
        "unit_price": "50.00",
        "total_amount": "100.00"
    }

@pytest.fixture
def sample_raw_dataset(test_config: Config) -> Path:
    """
    Creates a mock raw CSV landing dataset containing 3 valid and 2 invalid records.
    """
    records = [
        # Valid 1
        {
            "order_id": "ORD-101",
            "customer_id": "CUST-01",
            "customer_email": "alice@example.com",
            "product_category": "Books",
            "order_date": "2026-09-18",
            "quantity": 1,
            "unit_price": 20.00,
            "total_amount": 20.00
        },
        # Valid 2
        {
            "order_id": "ORD-102",
            "customer_id": "CUST-02",
            "customer_email": "bob@example.com",
            "product_category": "Home",
            "order_date": "2026-09-19",
            "quantity": 3,
            "unit_price": 15.50,
            "total_amount": 46.50
        },
        # Invalid 1 (negative price)
        {
            "order_id": "ORD-103",
            "customer_id": "CUST-03",
            "customer_email": "charlie@example.com",
            "product_category": "Sports",
            "order_date": "2026-09-19",
            "quantity": 2,
            "unit_price": -5.00,
            "total_amount": -10.00
        },
        # Invalid 2 (math inconsistency)
        {
            "order_id": "ORD-104",
            "customer_id": "CUST-04",
            "customer_email": "daniel@example.com",
            "product_category": "Electronics",
            "order_date": "2026-09-20",
            "quantity": 1,
            "unit_price": 100.00,
            "total_amount": 150.00
        }
    ]
    df = pd.DataFrame(records)
    file_path = test_config.raw_dir / "test_raw_batch.csv"
    df.to_csv(file_path, index=False)
    return file_path
