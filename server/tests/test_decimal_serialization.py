"""Test Decimal serialization for financial fields."""

from decimal import Decimal
from cvrgpt_api.models import AccountsSnapshot, AccountsDelta
from cvrgpt_api.models_finance import AccountLine
import json


def test_accounts_snapshot_decimal_serializes_as_string():
    """Test that Decimal values in AccountsSnapshot serialize as strings."""
    snapshot = AccountsSnapshot(
        revenue=Decimal("1234567.89"),
        ebit=Decimal("123456.78"),
        net_income=Decimal("98765.43"),
        assets=Decimal("5000000.00"),
        equity=Decimal("2500000.00")
    )
    
    # Test JSON serialization
    json_str = snapshot.model_dump_json()
    parsed = json.loads(json_str)
    
    # Verify values are strings, not floats
    assert parsed["revenue"] == "1234567.89"
    assert parsed["ebit"] == "123456.78"
    assert parsed["net_income"] == "98765.43"
    assert parsed["assets"] == "5000000.00"
    assert parsed["equity"] == "2500000.00"


def test_accounts_delta_decimal_serializes_as_string():
    """Test that Decimal values in AccountsDelta serialize as strings."""
    delta = AccountsDelta(
        field="revenue",
        current_value=Decimal("1234567.89"),
        previous_value=Decimal("1000000.00"),
        absolute_change=Decimal("234567.89"),
        percentage_change=Decimal("23.46")
    )
    
    json_str = delta.model_dump_json()
    parsed = json.loads(json_str)
    
    assert parsed["current_value"] == "1234567.89"
    assert parsed["previous_value"] == "1000000.00"
    assert parsed["absolute_change"] == "234567.89"
    assert parsed["percentage_change"] == "23.46"


def test_account_line_decimal_serializes_as_string():
    """Test that AccountLine with Decimal value serializes as string."""
    line = AccountLine(
        metric="revenue",
        value=Decimal("1234.56"),
        currency="DKK",
        period="2024"
    )
    
    json_str = line.model_dump_json()
    parsed = json.loads(json_str)
    
    # Verify the value is serialized as a string
    assert parsed["value"] == "1234.56"
    assert parsed["metric"] == "revenue"
    assert parsed["currency"] == "DKK"
    assert parsed["period"] == "2024"


def test_none_decimal_values_serialize_correctly():
    """Test that None Decimal values serialize correctly."""
    snapshot = AccountsSnapshot(
        revenue=None,
        ebit=Decimal("100.00"),
        net_income=None
    )
    
    json_str = snapshot.model_dump_json()
    parsed = json.loads(json_str)
    
    assert parsed["revenue"] is None
    assert parsed["ebit"] == "100.00"
    assert parsed["net_income"] is None


def test_decimal_precision_preserved():
    """Test that Decimal precision is preserved in serialization."""
    # Test various precision levels
    values = [
        Decimal("0.01"),  # 2 decimal places
        Decimal("1234.567890"),  # 6 decimal places
        Decimal("1000000"),  # No decimal places
        Decimal("0.123456789012345"),  # High precision
    ]
    
    for value in values:
        snapshot = AccountsSnapshot(revenue=value)
        json_str = snapshot.model_dump_json()
        parsed = json.loads(json_str)
        
        # Verify the string representation matches the original Decimal
        assert parsed["revenue"] == str(value)
