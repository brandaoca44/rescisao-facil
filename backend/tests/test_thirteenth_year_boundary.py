from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.termination import TerminationCalculationInput
from app.services.termination_service import calculate_termination

from app.domain.accrual import calculate_thirteenth_accrued_months_by_year


@pytest.mark.parametrize(("admission", "termination", "projected", "expected"), [
    ("2024-01-10", "2026-08-20", "2026-09-25", {2026: 9}),
    ("2024-01-10", "2026-12-20", "2027-01-25", {2026: 12, 2027: 1}),
    ("2024-01-10", "2026-12-01", "2027-01-14", {2026: 12, 2027: 0}),
    ("2024-01-10", "2026-12-01", "2027-01-15", {2026: 12, 2027: 1}),
    ("2026-12-18", "2026-12-20", "2027-01-19", {2026: 0, 2027: 1}),
    ("2026-12-17", "2026-12-20", "2027-01-19", {2026: 1, 2027: 1}),
    ("2024-01-10", "2026-12-20", "2026-12-20", {2026: 12}),
    ("2000-01-01", "2026-12-20", "2027-03-20", {2026: 12, 2027: 3}),
])
def test_thirteenth_allocates_each_year_without_losing_previous_months(
    admission, termination, projected, expected,
):
    assert calculate_thirteenth_accrued_months_by_year(
        date.fromisoformat(admission), date.fromisoformat(termination),
        date.fromisoformat(projected),
    ) == expected


@pytest.mark.parametrize(("admission", "termination", "projected"), [
    (date(2026, 12, 21), date(2026, 12, 20), date(2027, 1, 20)),
    (date(2024, 1, 1), date(2026, 12, 20), date(2026, 12, 19)),
])
def test_annual_thirteenth_rejects_inconsistent_dates(admission, termination, projected):
    with pytest.raises(ValueError):
        calculate_thirteenth_accrued_months_by_year(admission, termination, projected)


PAYLOAD = {
    "monthly_salary": "3000.00", "admission_date": "2024-01-10",
    "termination_date": "2026-12-20", "termination_type": "dismissal_without_cause",
    "notice_period_type": "indemnified",
}


def test_service_keeps_december_salary_and_adds_january_projection():
    result = calculate_termination(TerminationCalculationInput(**PAYLOAD))
    assert result.projected_termination_date == date(2027, 1, 25)
    assert [(item.year, item.accrued_months, item.value) for item in result.thirteenth_salary_by_year] == [
        (2026, 12, Decimal("3000.00")), (2027, 1, Decimal("250.00")),
    ]
    assert result.thirteenth_salary == Decimal("3250.00")
    assert result.inss_thirteenth == Decimal("278.60")
    assert result.fgts_termination_deposit == Decimal("708.00")
    assert result.total == Decimal("9183.33")
    assert result.net_total == Decimal("8749.04")


@pytest.mark.parametrize(("termination", "projected", "next_year_months", "expected"), [
    ("2026-12-12", "2027-01-14", 0, "3000.00"),
    ("2026-12-13", "2027-01-15", 1, "3250.00"),
])
def test_api_counts_january_only_after_fifteen_projected_days(
    termination, projected, next_year_months, expected,
):
    response = TestClient(app).post("/api/v1/terminations/calculate", json={
        **PAYLOAD, "admission_date": "2025-01-10", "termination_date": termination,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["projected_termination_date"] == projected
    assert data["thirteenth_salary"] == expected
    assert data["thirteenth_salary_by_year"][0]["accrued_months"] == 12
    assert data["thirteenth_salary_by_year"][1]["accrued_months"] == next_year_months


@pytest.mark.parametrize(("kind", "notice", "expected", "year_count"), [
    ("dismissal_without_cause", None, "3250.00", 2),
    ("dismissal_without_cause", "worked", "3000.00", 1),
    ("mutual_agreement", "indemnified", "3250.00", 2),
    ("mutual_agreement", "worked", "3000.00", 1),
    ("resignation", "worked", "3000.00", 1),
    ("resignation", "not_worked", "3000.00", 1),
    ("dismissal_with_cause", None, "0.00", 0),
])
def test_modes_preserve_notice_projection_and_year_allocation(kind, notice, expected, year_count):
    response = TestClient(app).post("/api/v1/terminations/calculate", json={
        **PAYLOAD, "termination_type": kind, "notice_period_type": notice,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["thirteenth_salary"] == expected
    assert len(data["thirteenth_salary_by_year"]) == year_count
    assert sum((Decimal(item["value"]) for item in data["thirteenth_salary_by_year"]), Decimal("0.00")) == Decimal(expected)
    if kind == "mutual_agreement" and notice == "indemnified":
        assert data["notice_period_value"] == "1800.00"
        assert data["projected_termination_date"] == "2027-01-25"


def test_higher_salary_updates_tax_and_fgts_from_full_thirteenth_amount():
    response = TestClient(app).post("/api/v1/terminations/calculate", json={
        **PAYLOAD, "monthly_salary": "9000.00",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["thirteenth_salary"] == "9750.00"
    assert data["inss_thirteenth"] == "988.09"
    assert data["irrf_thirteenth"] == "1500.80"
    assert data["fgts_termination_deposit"] == "2124.00"
    assert data["total"] == "27550.00"
    assert data["net_total"] == "24034.50"


def test_long_notice_can_cover_three_months_without_including_old_years():
    result = calculate_termination(TerminationCalculationInput(**{
        **PAYLOAD, "admission_date": "2000-01-01",
    }))
    assert result.notice_period_days == 90
    assert result.projected_termination_date == date(2027, 3, 20)
    assert [(item.year, item.accrued_months) for item in result.thirteenth_salary_by_year] == [(2026, 12), (2027, 3)]
    assert result.thirteenth_salary == Decimal("3750.00")


def test_year_values_round_individually_and_sum_exactly():
    result = calculate_termination(TerminationCalculationInput(**{
        **PAYLOAD, "monthly_salary": "1000.01",
    }))
    assert [item.value for item in result.thirteenth_salary_by_year] == [Decimal("1000.01"), Decimal("83.33")]
    assert result.thirteenth_salary == Decimal("1083.34")


def test_projection_into_2027_does_not_enable_2027_termination_tables():
    response = TestClient(app).post("/api/v1/terminations/calculate", json={
        **PAYLOAD, "termination_date": "2027-01-20",
    })
    assert response.status_code == 422


def test_openapi_exposes_annual_breakdown():
    response = TestClient(app).get("/openapi.json")
    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    assert "thirteenth_salary_by_year" in schemas["TerminationCalculationResult"]["required"]
    assert set(schemas["ThirteenthSalaryYearResult"]["properties"]) == {"year", "accrued_months", "value"}
