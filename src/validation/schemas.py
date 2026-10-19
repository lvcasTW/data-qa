from datetime import datetime, date, timezone
from typing import List, Tuple, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator

# Allowed product categories
ALLOWED_CATEGORIES = {"Electronics", "Home", "Clothing", "Books", "Sports"}

class OrderValidationModel(BaseModel):
    """
    Schema for validating an E-commerce Order.
    This model enforces strict data quality rules.
    """
    order_id: str = Field(..., min_length=1, description="Order ID cannot be empty")
    customer_id: str = Field(..., min_length=1, description="Customer ID cannot be empty")
    customer_email: EmailStr = Field(..., description="Must be a valid email address")
    product_category: str = Field(..., description="Category must be from the allowed list")
    order_date: date = Field(..., description="Order date is required and must be valid")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than zero")
    unit_price: float = Field(..., gt=0.0, description="Unit price must be greater than 0.0")
    total_amount: float = Field(..., gt=0.0, description="Total amount must be greater than 0.0")

    @field_validator("product_category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        # Standardize category name (capitalize) and check allowed list
        clean_value = value.strip().title()
        if clean_value not in ALLOWED_CATEGORIES:
            raise ValueError(f"Category '{value}' is not allowed. Choose from {ALLOWED_CATEGORIES}")
        return clean_value

    @field_validator("order_date", mode="before")
    @classmethod
    def parse_and_validate_date(cls, value: Any) -> date:
        # Support string parsing
        if isinstance(value, str):
            try:
                # Assuming YYYY-MM-DD
                parsed_date = datetime.strptime(value.strip(), "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Date '{value}' is not in format YYYY-MM-DD")
        elif isinstance(value, (datetime, date)):
            parsed_date = value if isinstance(value, date) else value.date()
        else:
            raise ValueError(f"Invalid date format: {value}")

        # Rule: Order date cannot be in the future
        if parsed_date > date.today():
            raise ValueError(f"Order date '{parsed_date}' cannot be in the future")
        return parsed_date

    @model_validator(mode="after")
    def validate_totals(self) -> 'OrderValidationModel':
        # Rule: check if total_amount is approximately equal to quantity * unit_price
        expected = round(self.quantity * self.unit_price, 2)
        actual = round(self.total_amount, 2)
        if abs(expected - actual) > 0.05:  # Allow 5 cents margin for potential floating rounding
            raise ValueError(f"Mathematical inconsistency: expected {expected} (quantity={self.quantity} * price={self.unit_price}), but got total_amount={actual}")
        return self


def validate_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates a list of dictionaries (raw records).
    
    Returns:
        Tuple:
            - List of valid records (fully parsed and typed)
            - List of quarantined records (with 'quarantine_reason' and 'quarantined_at')
    """
    valid_records = []
    quarantined_records = []

    for index, raw_record in enumerate(records):
        try:
            # We copy the record so we don't mutate the original input
            record_copy = raw_record.copy()
            # Validate using Pydantic model
            validated_model = OrderValidationModel(**record_copy)
            
            # Convert validated model to a dictionary with clean types
            clean_record = validated_model.model_dump()
            # Ensure date is serialized as string for output compatibility (e.g. CSV writes)
            clean_record["order_date"] = clean_record["order_date"].isoformat()
            
            valid_records.append(clean_record)
        except Exception as e:
            # Capture error details and quarantine the record
            failed_record = raw_record.copy()
            failed_record["quarantine_reason"] = str(e)
            failed_record["quarantined_at"] = datetime.now(timezone.utc).isoformat()
            failed_record["row_index"] = index
            quarantined_records.append(failed_record)

    return valid_records, quarantined_records
