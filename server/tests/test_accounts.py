from cvrgpt_core.models import Accounts
from cvrgpt_core.services.accounts import compare

def test_compare_basic():
    a = Accounts(year=2024, revenue=10.0, ebit=3.0, equity=None)
    b = Accounts(year=2023, revenue=7.0, ebit=2.0, equity=1.0)
    out = compare(a, b)
    assert out.deltas["revenue"] == 3.0
    assert out.deltas["ebit"] == 1.0
    assert out.deltas["equity"] is None
