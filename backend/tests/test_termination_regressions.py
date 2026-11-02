from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domain.accrual import (
    calculate_completed_vacation_periods,
    calculate_current_vacation_period_start,
    calculate_vacation_accrued_months,
)
from app.domain.notice_period import calculate_notice_period_days
from app.domain.salary_balance import calculate_salary_balance_for_dates
from app.domain.vacation import validate_vacation_periods


client = TestClient(app)
ENDPOINT = "/api/v1/terminations/calculate"
PAYLOAD = {
    "monthly_salary": "3000.00",
    "admission_date": "2024-01-10",
    "termination_date": "2026-08-20",
    "termination_type": "resignation",
    "notice_period_type": "worked",
}


@pytest.mark.parametrize(("admission", "termination", "expected"), [
    ("2026-08-15", "2026-08-20", "600.00"),
    ("2026-08-20", "2026-08-20", "100.00"),
    ("2026-08-31", "2026-08-31", "100.00"),
    ("2024-01-10", "2026-08-31", "3000.00"),
    ("2024-01-10", "2026-02-28", "3000.00"),
    ("2024-02-01", "2024-02-29", "3000.00"),
    ("2026-02-15", "2026-02-28", "1400.00"),
])
def test_salary_counts_only_the_worked_interval(admission, termination, expected):
    assert calculate_salary_balance_for_dates(
        Decimal("3000.00"), date.fromisoformat(admission), date.fromisoformat(termination),
    ) == Decimal(expected)


@pytest.mark.parametrize(("termination", "expected"), [
    (date(2025, 2, 28), 30),
    (date(2025, 3, 1), 33),
    (date(2026, 2, 28), 33),
    (date(2026, 3, 1), 36),
    (date(2028, 2, 29), 42),
])
def test_leap_day_notice_anniversary(termination, expected):
    assert calculate_notice_period_days(date(2024, 2, 29), termination) == expected


@pytest.mark.parametrize(("reference", "completed", "start"), [
    (date(2026, 1, 8), 0, date(2025, 1, 10)),
    (date(2026, 1, 9), 1, date(2026, 1, 10)),
    (date(2026, 1, 10), 1, date(2026, 1, 10)),
])
def test_vacation_period_includes_last_worked_day(reference, completed, start):
    admission = date(2025, 1, 10)
    assert calculate_completed_vacation_periods(admission, reference) == completed
    assert calculate_current_vacation_period_start(admission, reference) == start
    if completed:
        assert calculate_vacation_accrued_months(admission, reference) == 0


def test_leap_vacation_period_returns_to_original_anniversary():
    admission = date(2024, 2, 29)
    assert calculate_current_vacation_period_start(admission, date(2027, 3, 1)) == date(2027, 3, 1)
    assert calculate_current_vacation_period_start(admission, date(2028, 2, 29)) == date(2028, 2, 29)


@pytest.mark.parametrize(("admission", "reference", "acquired", "overdue"), [
    (date(2026, 8, 15), date(2026, 8, 20), 1, 0),
    (date(2025, 1, 10), date(2026, 8, 20), 1, 1),
    (date(2025, 1, 10), date(2026, 8, 20), 0, 1),
])
def test_rejects_incompatible_vacation_periods(admission, reference, acquired, overdue):
    with pytest.raises(ValueError):
        validate_vacation_periods(admission, reference, acquired, overdue)


def test_accepts_acquired_and_overdue_without_double_counting():
    validate_vacation_periods(date(2024, 1, 10), date(2026, 8, 20), 1, 1)


@pytest.mark.parametrize("termination_type", [
    "dismissal_without_cause", "resignation", "mutual_agreement", "dismissal_with_cause",
])
@pytest.mark.parametrize(("admission", "termination", "expected"), [
    ("2026-08-15", "2026-08-20", "600.00"),
    ("2024-01-10", "2026-08-31", "3000.00"),
    ("2024-02-29", "2026-08-20", "2000.00"),
])
def test_calendar_regressions_through_api(termination_type, admission, termination, expected):
    payload = {**PAYLOAD, "termination_type": termination_type,
               "admission_date": admission, "termination_date": termination}
    payload.pop("notice_period_type")
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 200
    assert response.json()["salary_balance"] == expected


@pytest.mark.parametrize("field", ["monthly_salary", "fgts_rescission_base"])
@pytest.mark.parametrize("value", ["1e100", "NaN", "Infinity", "-1", "0.001"])
def test_invalid_money_returns_validation_error(field, value):
    response = client.post(ENDPOINT, json={**PAYLOAD, field: value})
    assert response.status_code == 422


def test_highest_supported_money_does_not_overflow():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "monthly_salary": "9999999999.99", "fgts_rescission_base": "9999999999.99",
    })
    assert response.status_code == 200
    assert Decimal(response.json()["net_total"]).is_finite()


@pytest.mark.parametrize("termination", ["2025-08-20", "9999-12-31"])
def test_unsupported_year_is_rejected_before_calendar_operations(termination):
    response = client.post(ENDPOINT, json={**PAYLOAD, "termination_date": termination})
    assert response.status_code == 422


@pytest.mark.parametrize(("changes", "message"), [
    ({"admission_date": "2026-09-01"}, "before admission"),
    ({"admission_date": "2026-08-15", "acquired_vacation_periods": 10}, "acquisition periods"),
    ({"admission_date": "2025-08-15", "overdue_vacation_periods": 1}, "concession period"),
])
def test_domain_validation_through_api(changes, message):
    response = client.post(ENDPOINT, json={**PAYLOAD, **changes})
    assert response.status_code == 400
    assert message in response.json()["detail"]


@pytest.mark.parametrize("termination_type", [
    "dismissal_without_cause", "resignation", "mutual_agreement", "dismissal_with_cause",
])
@pytest.mark.parametrize("notice", [None, "worked", "indemnified", "not_worked"])
def test_notice_matrix_and_net_total_through_api(termination_type, notice):
    allowed = {
        "dismissal_without_cause": {None, "worked", "indemnified"},
        "resignation": {None, "worked", "not_worked"},
        "mutual_agreement": {None, "worked", "indemnified"},
        "dismissal_with_cause": {None},
    }
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "termination_type": termination_type, "notice_period_type": notice,
    })
    if notice not in allowed[termination_type]:
        assert response.status_code == 400
        return
    assert response.status_code == 200
    data = response.json()
    assert Decimal(data["net_total"]) == (
        Decimal(data["total"]) - Decimal(data["inss_total"])
        - Decimal(data["irrf_total"]) - Decimal(data["notice_period_discount"])
    )
    if notice == "not_worked":
        assert data["notice_period_discount"] == "3000.00"
        assert data["notice_period_value"] == "0.00"
    if notice == "worked":
        assert data["projected_termination_date"] == PAYLOAD["termination_date"]
        assert data["notice_period_value"] == "0.00"


def test_vacation_validation_uses_indemnified_projection():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "admission_date": "2025-09-10",
        "termination_type": "dismissal_without_cause",
        "notice_period_type": "indemnified", "acquired_vacation_periods": 1,
    })
    assert response.status_code == 200
    assert response.json()["acquired_vacation"] == "3000.00"


def test_vacation_anniversary_does_not_pay_same_period_twice():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "admission_date": "2025-08-21", "acquired_vacation_periods": 1,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["acquired_vacation"] == "3000.00"
    assert data["proportional_vacation"] == "0.00"


def test_mutual_agreement_rounds_half_cent_explicitly():
    response = client.post(ENDPOINT, json={
        **PAYLOAD, "monthly_salary": "0.05",
        "admission_date": "2026-08-01",
        "termination_type": "mutual_agreement",
        "notice_period_type": "indemnified",
    })
    assert response.status_code == 200
    assert response.json()["notice_period_value"] == "0.03"


def test_salary_date_calculation_rejects_reversed_interval():
    with pytest.raises(ValueError):
        calculate_salary_balance_for_dates(
            Decimal("3000.00"), date(2026, 9, 1), date(2026, 8, 20),
        )
