from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.termination import TerminationCalculationInput
from app.services.termination_service import calculate_termination


client = TestClient(app)
ENDPOINT = "/api/v1/terminations/calculate"
PAYLOAD = {
    "monthly_salary": "3000.00",
    "admission_date": "2024-01-10",
    "termination_date": "2026-08-20",
    "acquired_vacation_periods": 1,
    "overdue_vacation_periods": 1,
    "fgts_rescission_base": "10000.00",
}
CASES = [
    ("dismissal_without_cause", "1.00", True, "22850.00", "22516.12"),
    ("resignation", "0.00", False, "18333.33", "18021.95"),
    ("mutual_agreement", "0.80", False, "21050.00", "20716.12"),
    ("dismissal_with_cause", "0.00", False, "14000.00", "13844.31"),
]


@pytest.mark.parametrize(("kind", "rate", "insurance", "gross", "net"), CASES)
def test_service_exposes_benefits_and_preserves_financial_totals(kind, rate, insurance, gross, net):
    data = TerminationCalculationInput(**PAYLOAD, termination_type=kind)
    result = calculate_termination(data)
    assert result.benefits.fgts_withdrawal_rate_under_saque_rescisao == Decimal(rate)
    assert result.benefits.unemployment_insurance_possible_by_termination_type is insurance
    assert result.benefits.notes
    assert result.total == Decimal(gross)
    assert result.net_total == Decimal(net)


@pytest.mark.parametrize(("kind", "rate", "insurance", "gross", "net"), CASES)
def test_api_serializes_benefits_without_changing_existing_totals(kind, rate, insurance, gross, net):
    response = client.post(ENDPOINT, json={**PAYLOAD, "termination_type": kind})
    assert response.status_code == 200
    data = response.json()
    benefits = data["benefits"]
    assert benefits["fgts_withdrawal_rate_under_saque_rescisao"] == rate
    assert benefits["unemployment_insurance_possible_by_termination_type"] is insurance
    assert isinstance(benefits["notes"], list) and benefits["notes"]
    assert data["total"] == gross
    assert data["net_total"] == net


def test_benefits_do_not_use_fgts_penalty_base_as_available_balance():
    first = calculate_termination(TerminationCalculationInput(
        **{**PAYLOAD, "fgts_rescission_base": "0.00"},
        termination_type="dismissal_without_cause",
    ))
    second = calculate_termination(TerminationCalculationInput(
        **PAYLOAD, termination_type="dismissal_without_cause",
    ))
    assert first.benefits == second.benefits
    assert first.fgts_penalty == Decimal("0.00")
    assert second.fgts_penalty == Decimal("4000.00")
    assert first.total == second.total
    assert first.net_total == second.net_total


def test_benefits_do_not_guarantee_insurance_for_short_contract():
    response = client.post(ENDPOINT, json={
        "monthly_salary": "3000.00", "admission_date": "2026-08-15",
        "termination_date": "2026-08-20", "termination_type": "dismissal_without_cause",
    })
    assert response.status_code == 200
    benefits = response.json()["benefits"]
    assert benefits["unemployment_insurance_possible_by_termination_type"] is True
    assert any("histórico salarial" in note for note in benefits["notes"])


def test_openapi_documents_benefits_conditions_without_new_inputs():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    assert "benefits" in schemas["TerminationCalculationResult"]["required"]
    fields = schemas["TerminationBenefitsResult"]["properties"]
    assert "saque-aniversário" in fields["fgts_withdrawal_rate_under_saque_rescisao"]["description"]
    assert "Não avalia" in fields["unemployment_insurance_possible_by_termination_type"]["description"]
    assert "benefits" not in schemas["TerminationCalculationInput"]["properties"]
