from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.termination import TerminationCalculationInput
from app.services.termination_service import calculate_termination


client = TestClient(app)
ENDPOINT = "/api/v1/terminations/calculate"
PAYLOAD = {
    "monthly_salary": "3000.00", "admission_date": "2024-01-10",
    "termination_date": "2026-12-20", "termination_type": "dismissal_without_cause",
    "notice_period_type": "indemnified",
}


def calculate(previous=None, **changes):
    payload = {**PAYLOAD, **changes}
    if previous is not None:
        payload["thirteenth_previous_payment"] = previous
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_default_history_preserves_all_current_results():
    assert calculate() == calculate({}) == calculate({
        "gross_amount": "0.00", "inss_withheld": "0.00",
        "irrf_withheld": "0.00", "fgts_deposited": "0.00",
    })


def test_fully_paid_current_year_preserves_next_year_projection():
    result = calculate({
        "gross_amount": "3000.00", "inss_withheld": "248.60",
        "fgts_deposited": "240.00",
    })
    assert result["thirteenth_salary"] == "3250.00"
    assert result["thirteenth_salary_by_year"][1]["value"] == "250.00"
    assert result["thirteenth_settlement"]["gross_balance"] == "250.00"
    assert result["thirteenth_settlement"]["inss_assessed"] == "278.60"
    assert result["inss_thirteenth"] == "30.00"
    assert result["fgts_termination_deposit"] == "468.00"
    assert result["total"] == "9183.33"
    assert result["net_total"] == "5997.64"


def test_plain_advance_keeps_full_inss_and_irrf_bases():
    base = calculate()
    result = calculate({"gross_amount": "1500.00", "fgts_deposited": "120.00"})
    assert result["total"] == base["total"]
    assert result["inss_thirteenth"] == base["inss_thirteenth"] == "278.60"
    assert result["irrf_thirteenth"] == base["irrf_thirteenth"]
    assert Decimal(result["net_total"]) == Decimal(base["net_total"]) - Decimal("1500.00")
    assert result["fgts_termination_deposit"] == "588.00"


def test_high_income_deducts_only_additional_tax_and_fgts():
    result = calculate({
        "gross_amount": "9000.00", "inss_withheld": "988.09",
        "irrf_withheld": "1294.55", "fgts_deposited": "720.00",
    }, monthly_salary="9000.00")
    assert result["thirteenth_salary"] == "9750.00"
    assert result["inss_thirteenth"] == "0.00"
    assert result["irrf_thirteenth"] == "206.25"
    assert result["thirteenth_settlement"]["irrf_assessed"] == "1500.80"
    assert result["fgts_termination_deposit"] == "1404.00"
    assert result["net_total"] == "17317.14"


def test_already_paid_thirteenth_does_not_duplicate_small_exclusive_tax():
    result = calculate({
        "gross_amount": "5027.89", "inss_withheld": "505.42", "irrf_withheld": "9.99",
        "fgts_deposited": "402.23",
    }, monthly_salary="5027.89", termination_date="2026-12-30",
       termination_type="resignation", notice_period_type="worked")
    assert result["thirteenth_settlement"]["gross_balance"] == "0.00"
    assert result["thirteenth_settlement"]["irrf_assessed"] == "9.99"
    assert result["irrf_thirteenth"] == "0.00"
    assert result["inss_thirteenth"] == "0.00"


@pytest.mark.parametrize("field", ["gross_amount", "inss_withheld", "irrf_withheld", "fgts_deposited"])
@pytest.mark.parametrize("value", ["-1.00", "0.001", "1e100", "NaN", "Infinity"])
def test_invalid_money_in_history_is_rejected(field, value):
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "thirteenth_previous_payment": {field: value},
    })
    assert response.status_code == 422


@pytest.mark.parametrize("previous", [
    {"gross_amount": "3000.01"},
    {"gross_amount": "3000.00", "inss_withheld": "278.61"},
    {"gross_amount": "3000.00", "irrf_withheld": "0.01"},
    {"gross_amount": "3000.00", "fgts_deposited": "240.01"},
    {"inss_withheld": "1.00"},
    {"fgts_deposited": "1.00"},
])
def test_incompatible_history_returns_domain_error(previous):
    response = client.post(ENDPOINT, json={**PAYLOAD, "thirteenth_previous_payment": previous})
    assert response.status_code == 400


def test_history_cannot_be_used_for_other_years_or_silent_typo_fields():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "thirteenth_previous_payment": {"year": 2027, "gross_amount": "250.00"},
    })
    assert response.status_code == 422


def test_positive_history_without_thirteenth_entitlement_is_explicitly_unsupported():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "termination_type": "dismissal_with_cause", "notice_period_type": None,
        "thirteenth_previous_payment": {"gross_amount": "100.00"},
    })
    assert response.status_code == 400


def test_service_updates_tax_totals_and_net_consistently():
    result = calculate_termination(TerminationCalculationInput(**PAYLOAD, thirteenth_previous_payment={
        "gross_amount": "3000.00", "inss_withheld": "248.60", "fgts_deposited": "240.00",
    }))
    assert result.inss_total == result.inss_monthly + result.inss_thirteenth
    assert result.irrf_total == result.irrf_monthly + result.irrf_thirteenth
    assert result.net_total == (
        result.total - result.inss_total - result.irrf_total
        - result.notice_period_discount - result.thirteenth_settlement.gross_paid
    )


def test_openapi_describes_optional_history_and_settlement():
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert "thirteenth_previous_payment" not in schemas["TerminationCalculationInput"]["required"]
    assert schemas["ThirteenthPreviousPaymentInput"]["additionalProperties"] is False
    assert "thirteenth_settlement" in schemas["TerminationCalculationResult"]["required"]
