from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.termination import TerminationCalculationInput
from app.services.termination_service import calculate_termination

from app.domain.accrual import (
    calculate_completed_vacation_periods,
    calculate_overdue_vacation_periods,
    calculate_vacation_accrued_months,
)
from app.domain.vacation import validate_vacation_periods


@pytest.mark.parametrize("admission_day", [29, 30, 31])
@pytest.mark.parametrize(("termination", "expected"), [
    (date(2026, 2, 28), 1),
    (date(2026, 3, 14), 1),
    (date(2026, 3, 15), 2),
])
def test_missing_february_day_uses_first_subsequent_day(admission_day, termination, expected):
    assert calculate_vacation_accrued_months(date(2026, 1, admission_day), termination) == expected


@pytest.mark.parametrize(("admission_day", "termination", "expected"), [
    (29, date(2026, 4, 11), 2), (29, date(2026, 4, 12), 3),
    (30, date(2026, 4, 12), 2), (30, date(2026, 4, 13), 3),
    (31, date(2026, 4, 13), 2), (31, date(2026, 4, 14), 3),
    (31, date(2026, 6, 13), 4), (31, date(2026, 6, 14), 5),
])
def test_later_months_keep_original_day_after_february(admission_day, termination, expected):
    assert calculate_vacation_accrued_months(date(2026, 1, admission_day), termination) == expected


@pytest.mark.parametrize(("admission", "termination", "expected"), [
    (date(2024, 1, 29), date(2024, 3, 13), 1),
    (date(2024, 1, 29), date(2024, 3, 14), 2),
    (date(2024, 1, 30), date(2024, 3, 14), 1),
    (date(2024, 1, 30), date(2024, 3, 15), 2),
    (date(2024, 2, 29), date(2024, 4, 11), 1),
    (date(2024, 2, 29), date(2024, 4, 12), 2),
])
def test_leap_year_and_fifteen_day_boundaries(admission, termination, expected):
    assert calculate_vacation_accrued_months(admission, termination) == expected


@pytest.mark.parametrize(("reference", "completed", "overdue"), [
    (date(2026, 1, 8), 1, 0),
    (date(2026, 1, 9), 2, 0),
    (date(2026, 1, 10), 2, 1),
    (date(2027, 1, 9), 3, 1),
    (date(2027, 1, 10), 3, 2),
])
def test_acquisition_completion_and_concession_expiry_have_distinct_dates(reference, completed, overdue):
    admission = date(2024, 1, 10)
    assert calculate_completed_vacation_periods(admission, reference) == completed
    assert calculate_overdue_vacation_periods(admission, reference) == overdue


def test_does_not_allow_overdue_on_last_day_of_concession_period():
    with pytest.raises(ValueError, match="expired concession period"):
        validate_vacation_periods(date(2024, 1, 10), date(2026, 1, 9), 1, 1)
    validate_vacation_periods(date(2024, 1, 10), date(2026, 1, 10), 1, 1)


def test_prevents_expired_period_from_being_declared_as_simple_payment():
    with pytest.raises(ValueError, match="within the concession period"):
        validate_vacation_periods(date(2024, 1, 10), date(2026, 8, 20), 2, 0)
    validate_vacation_periods(date(2024, 1, 10), date(2026, 8, 20), 1, 1)


def test_two_simple_periods_fit_only_on_the_shared_boundary_day():
    validate_vacation_periods(date(2024, 1, 10), date(2026, 1, 9), 2, 0)
    with pytest.raises(ValueError):
        validate_vacation_periods(date(2024, 1, 10), date(2026, 1, 10), 2, 0)


@pytest.mark.parametrize("admission_day", [29, 30, 31])
def test_complete_acquisition_is_not_also_paid_as_proportional(admission_day):
    admission = date(2025, 1, admission_day)
    completion = date(2026, 1, admission_day - 1)
    assert calculate_completed_vacation_periods(admission, completion) == 1
    assert calculate_vacation_accrued_months(admission, completion) == 0


def test_vacation_concession_expiry_handles_leap_day():
    admission = date(2024, 2, 29)
    assert calculate_overdue_vacation_periods(admission, date(2026, 2, 28)) == 0
    assert calculate_overdue_vacation_periods(admission, date(2026, 3, 1)) == 1


client = TestClient(app)
ENDPOINT = "/api/v1/terminations/calculate"
PAYLOAD = {
    "monthly_salary": "3000.00", "admission_date": "2024-09-10",
    "termination_date": "2026-08-07", "termination_type": "dismissal_without_cause",
    "notice_period_type": "indemnified",
}


@pytest.mark.parametrize("admission_day", [29, 30, 31])
def test_api_does_not_advance_vacation_avo_after_february(admission_day):
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "admission_date": f"2026-01-{admission_day}",
        "termination_date": "2026-03-14", "termination_type": "resignation",
        "notice_period_type": "worked",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["vacation_accrued_months"] == 1
    assert data["proportional_vacation"] == "250.00"
    assert data["proportional_vacation_bonus"] == "83.33"
    assert data["total"] == "1983.33"
    assert data["net_total"] == "1859.58"


@pytest.mark.parametrize(("termination", "acquired", "overdue", "expected_status"), [
    ("2026-08-07", 2, 0, 200),
    ("2026-08-07", 1, 1, 400),
    ("2026-08-08", 2, 0, 400),
    ("2026-08-08", 1, 1, 200),
])
def test_api_uses_projected_date_for_concession_boundary(termination, acquired, overdue, expected_status):
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "termination_date": termination,
        "acquired_vacation_periods": acquired, "overdue_vacation_periods": overdue,
    })
    assert response.status_code == expected_status
    if expected_status == 200:
        data = response.json()
        assert data["projected_termination_date"] == (
            "2026-09-09" if termination == "2026-08-07" else "2026-09-10"
        )
        assert data["proportional_vacation"] == "0.00"
        assert Decimal(data["acquired_vacation"]) == Decimal("3000.00") * acquired
        assert Decimal(data["overdue_vacation"]) == Decimal("6000.00") * overdue
        assert Decimal(data["overdue_vacation_bonus"]) == Decimal("2000.00") * overdue


def test_projection_completes_acquisition_without_duplicate_proportional_payment():
    result = calculate_termination(TerminationCalculationInput(**{
        **PAYLOAD, "admission_date": "2025-09-10", "termination_date": "2026-08-10",
        "acquired_vacation_periods": 1,
    }))
    assert result.projected_termination_date == date(2026, 9, 9)
    assert result.acquired_vacation == Decimal("3000.00")
    assert result.acquired_vacation_bonus == Decimal("1000.00")
    assert result.vacation_accrued_months == 0
    assert result.proportional_vacation == Decimal("0.00")
    assert result.total == Decimal("10000.00")
    assert result.net_total == Decimal("9769.31")


def test_unworked_notice_cannot_be_used_to_complete_vacation_acquisition():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "admission_date": "2025-09-10", "termination_date": "2026-08-10",
        "termination_type": "resignation", "notice_period_type": "not_worked",
        "acquired_vacation_periods": 1,
    })
    assert response.status_code == 400


@pytest.mark.parametrize("admission_day", [29, 30, 31])
def test_just_cause_keeps_full_vacation_and_excludes_proportional(admission_day):
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "admission_date": f"2025-01-{admission_day}",
        "termination_date": f"2026-01-{admission_day - 1}",
        "termination_type": "dismissal_with_cause", "notice_period_type": None,
        "acquired_vacation_periods": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["acquired_vacation"] == "3000.00"
    assert data["acquired_vacation_bonus"] == "1000.00"
    assert data["proportional_vacation"] == "0.00"


def test_overdue_vacation_includes_one_third_without_changing_tax_bases():
    payload = {**PAYLOAD, "termination_date": "2026-08-08"}
    first = client.post(ENDPOINT, json=payload)
    second = client.post(ENDPOINT, json={**payload, "overdue_vacation_periods": 1})
    assert first.status_code == second.status_code == 200
    base, extra = first.json(), second.json()
    assert extra["overdue_vacation"] == "6000.00"
    assert extra["overdue_vacation_bonus"] == "2000.00"
    assert Decimal(extra["total"]) - Decimal(base["total"]) == Decimal("8000.00")
    assert Decimal(extra["net_total"]) - Decimal(base["net_total"]) == Decimal("8000.00")
    for field in ("inss_total", "irrf_total", "fgts_termination_deposit"):
        assert extra[field] == base[field]


def test_openapi_explains_non_overlapping_periods_at_projected_date():
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    fields = schemas["TerminationCalculationInput"]["properties"]
    assert "data projetada" in fields["acquired_vacation_periods"]["description"]
    assert "Não incluir" in fields["overdue_vacation_periods"]["description"]
