import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from src.validation.schemas import OrderValidationModel, validate_records

def test_valid_order_pydantic_model(sample_valid_order_dict):
    """Verifies that a correct raw dictionary is successfully parsed and validated."""
    model = OrderValidationModel(**sample_valid_order_dict)
    assert model.order_id == "ORD-1234"
    assert model.customer_id == "CUST-999"
    assert model.customer_email == "test@example.com"
    assert model.product_category == "Electronics"
    assert model.order_date == date(2026, 9, 20)
    assert model.quantity == 2
    assert model.unit_price == 50.0
    assert model.total_amount == 100.0

def test_validation_fails_on_negative_quantity(sample_valid_order_dict):
    """Enforces that zero or negative quantity is rejected."""
    bad_data = sample_valid_order_dict.copy()
    bad_data["quantity"] = "0"
    with pytest.raises(ValidationError) as excinfo:
        OrderValidationModel(**bad_data)
    assert "greater than 0" in str(excinfo.value)

def test_validation_fails_on_negative_price(sample_valid_order_dict):
    """Enforces that negative unit prices are rejected."""
    bad_data = sample_valid_order_dict.copy()
    bad_data["unit_price"] = "-2.50"
    with pytest.raises(ValidationError) as excinfo:
        OrderValidationModel(**bad_data)
    assert "greater than 0" in str(excinfo.value)

def test_validation_fails_on_future_date(sample_valid_order_dict):
    """Enforces that order dates cannot be in the future."""
    tomorrow_str = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    bad_data = sample_valid_order_dict.copy()
    bad_data["order_date"] = tomorrow_str
    with pytest.raises(ValidationError) as excinfo:
        OrderValidationModel(**bad_data)
    assert "cannot be in the future" in str(excinfo.value)

def test_validation_fails_on_disallowed_category(sample_valid_order_dict):
    """Enforces that only categories in the ALLOWED_CATEGORIES set are accepted."""
    bad_data = sample_valid_order_dict.copy()
    bad_data["product_category"] = "Automotive"
    with pytest.raises(ValidationError) as excinfo:
        OrderValidationModel(**bad_data)
    assert "is not allowed" in str(excinfo.value)

def test_validation_capitalizes_valid_category(sample_valid_order_dict):
    """Ensures that category name spacing and capitalization are automatically standardized."""
    data = sample_valid_order_dict.copy()
    data["product_category"] = "  eLeCtRoNiCs  "
    model = OrderValidationModel(**data)
    assert model.product_category == "Electronics"

def test_validation_fails_on_math_inconsistency(sample_valid_order_dict):
    """Enforces mathematical checks: total_amount MUST equal quantity * unit_price."""
    bad_data = sample_valid_order_dict.copy()
    bad_data["total_amount"] = "150.00"  # 2 * 50 = 100, not 150!
    with pytest.raises(ValidationError) as excinfo:
        OrderValidationModel(**bad_data)
    assert "Mathematical inconsistency" in str(excinfo.value)

def test_validate_records_bulk_split():
    """
    Tests that the helper validate_records splits a mixed batch of data
    accurately into valid and quarantined lists.
    """
    batch = [
        # Valid
        {
            "order_id": "ORD-001",
            "customer_id": "CUST-A",
            "customer_email": "a@test.com",
            "product_category": "Books",
            "order_date": "2026-09-15",
            "quantity": 1,
            "unit_price": 10.00,
            "total_amount": 10.00,
        },
        # Invalid (invalid email)
        {
            "order_id": "ORD-002",
            "customer_id": "CUST-B",
            "customer_email": "bad_email_no_at",
            "product_category": "Home",
            "order_date": "2026-09-15",
            "quantity": 2,
            "unit_price": 5.00,
            "total_amount": 10.00,
        }
    ]
    
    valid, quarantined = validate_records(batch)
    
    assert len(valid) == 1
    assert valid[0]["order_id"] == "ORD-001"
    assert valid[0]["customer_email"] == "a@test.com"
    
    assert len(quarantined) == 1
    assert quarantined[0]["order_id"] == "ORD-002"
    assert "quarantine_reason" in quarantined[0]
    assert "value is not a valid email address" in quarantined[0]["quarantine_reason"]
