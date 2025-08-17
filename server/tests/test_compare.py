from cvrgpt_api.services.compare import compute_ratios, compare_accounts, narrate_compare


def test_ratios_and_compare():
    prev = {
        "pl": {"revenue": 100.0, "ebit": 10.0},
        "bs": {
            "assets": 200.0,
            "equity": 50.0,
            "current_assets": 80.0,
            "current_liabilities": 40.0,
        },
    }
    curr = {
        "pl": {"revenue": 120.0, "ebit": 18.0},
        "bs": {
            "assets": 220.0,
            "equity": 60.0,
            "current_assets": 100.0,
            "current_liabilities": 50.0,
        },
    }
    r_prev = compute_ratios(prev)
    r_curr = compute_ratios(curr)
    assert round(r_prev["margin"], 2) == 0.10
    assert round(r_curr["margin"], 2) == 0.15
    comp = compare_accounts(prev, curr)
    assert round(comp["delta"]["margin"], 2) == 0.05
    txt = narrate_compare(comp)
    assert "Margin" in txt and "Solvency" in txt and "Liquidity" in txt
