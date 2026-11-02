from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.domain.inss import calculate_inss_contribution, calculate_termination_inss
from app.domain.irrf import (
    calculate_irrf, calculate_monthly_irrf, calculate_termination_irrf,
)
from app.main import app


# INSS: faixas de 2026 e soma progressiva sem arredondamentos intermediários.
@pytest.mark.parametrize(("income", "expected"), [
    ("1620.99", "121.57"), ("1621.00", "121.58"), ("1621.01", "121.58"),
    ("2902.83", "236.94"), ("2902.84", "236.94"), ("2902.85", "236.94"),
    ("4354.26", "411.11"), ("4354.27", "411.11"), ("4354.28", "411.11"),
    ("8475.54", "988.09"), ("8475.55", "988.09"), ("8475.56", "988.09"),
])
def test_inss_at_each_progressive_boundary(income, expected):
    assert calculate_inss_contribution(Decimal(income), 2026) == Decimal(expected)


def test_monthly_and_thirteenth_each_have_their_own_inss_ceiling():
    monthly, thirteenth, total = calculate_termination_inss(
        Decimal("10000.00"), Decimal("10000.00"), 2026,
    )
    assert monthly == thirteenth == Decimal("988.09")
    assert total == Decimal("1976.18")


# Deduções informadas nos exemplos oficiais da Receita; não são fixtures do INSS.
@pytest.mark.parametrize(("income", "deduction", "expected"), [
    ("3036.00", "257.73", "0.00"),
    ("4000.00", "373.41", "0.00"),
    ("5000.00", "509.60", "0.00"),
    ("6000.00", "649.60", "382.88"),
    ("7607.20", "0.00", "1016.27"),
])
def test_irrf_matches_revenue_service_examples(income, deduction, expected):
    assert calculate_monthly_irrf(
        Decimal(income), Decimal(deduction), 2026,
    ) == Decimal(expected)


@pytest.mark.parametrize(("deduction", "raw", "withheld"), [
    ("5045.20", "9.99", "0.00"),
    ("5045.07", "10.00", "0.00"),
    ("5045.00", "10.01", "10.01"),
])
def test_monthly_retention_exemption_includes_exactly_ten_reais(deduction, raw, withheld):
    # Dedução controlada para isolar os centavos na fronteira da retenção.
    income = Decimal("7607.20")
    assert calculate_irrf(income, Decimal(deduction), 2026) == Decimal(raw)
    assert calculate_monthly_irrf(income, Decimal(deduction), 2026) == Decimal(withheld)
    monthly, thirteenth, total = calculate_termination_irrf(
        income, Decimal(deduction), income, Decimal(deduction), 2026,
    )
    assert monthly == Decimal(withheld)
    assert thirteenth == Decimal(raw)
    assert total == Decimal(withheld) + Decimal(raw)


@pytest.mark.parametrize("income", ["5000.01", "5027.89", "5027.94", "7350.00", "7350.01"])
def test_reduction_uses_gross_income_and_thirteenth_is_separate(income):
    income = Decimal(income)
    inss = calculate_inss_contribution(income, 2026)
    monthly, thirteenth, total = calculate_termination_irrf(income, inss, income, inss, 2026)
    raw = calculate_irrf(income, inss, 2026)
    assert thirteenth == raw
    assert monthly == (Decimal("0.00") if raw <= Decimal("10.00") else raw)
    assert total == monthly + thirteenth


def test_real_payroll_values_use_current_inss_before_irrf():
    # O INSS dos exemplos da Receita não deve substituir a tabela previdenciária.
    inss = calculate_inss_contribution(Decimal("6000.00"), 2026)
    assert inss == Decimal("641.51")
    assert calculate_monthly_irrf(Decimal("6000.00"), inss, 2026) == Decimal("385.10")


@pytest.mark.parametrize(("salary", "expected"), [("5027.89", "0.00"), ("5027.94", "10.01")])
def test_api_retention_boundary_changes_net_without_changing_gross(salary, expected):
    client = TestClient(app)
    response = client.post("/api/v1/terminations/calculate", json={
        "monthly_salary": salary, "admission_date": "2024-01-10",
        "termination_date": "2026-06-30", "termination_type": "resignation",
        "notice_period_type": "worked",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["salary_balance"] == salary
    assert data["irrf_monthly"] == expected
    assert Decimal(data["irrf_total"]) == Decimal(data["irrf_monthly"]) + Decimal(data["irrf_thirteenth"])
    assert Decimal(data["net_total"]) == (
        Decimal(data["total"]) - Decimal(data["inss_total"]) - Decimal(data["irrf_total"])
    )


def test_indemnified_vacation_and_fgts_do_not_enter_income_tax_bases():
    client = TestClient(app)
    payload = {
        "monthly_salary": "9000.00", "admission_date": "2024-01-10",
        "termination_date": "2026-08-20", "termination_type": "dismissal_without_cause",
        "notice_period_type": "indemnified",
    }
    base = client.post("/api/v1/terminations/calculate", json=payload).json()
    extra = client.post("/api/v1/terminations/calculate", json={
        **payload, "acquired_vacation_periods": 1, "overdue_vacation_periods": 1,
        "fgts_rescission_base": "100000.00",
    }).json()
    for field in ("inss_monthly", "inss_thirteenth", "irrf_monthly", "irrf_thirteenth"):
        assert extra[field] == base[field]
    assert Decimal(extra["total"]) > Decimal(base["total"])
    assert extra["fgts_penalty"] == "40000.00"


def test_api_keeps_small_thirteenth_tax_while_waiving_monthly_retention():
    client = TestClient(app)
    response = client.post("/api/v1/terminations/calculate", json={
        "monthly_salary": "5027.89", "admission_date": "2024-01-10",
        "termination_date": "2026-12-30", "termination_type": "resignation",
        "notice_period_type": "worked",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["thirteenth_salary"] == "5027.89"
    assert data["irrf_monthly"] == "0.00"
    assert data["irrf_thirteenth"] == "9.99"
    assert data["irrf_total"] == "9.99"
