from datetime import date

import pytest

from app.domain.accrual import (
    calculate_current_vacation_period_start,
    calculate_thirteenth_accrued_months,
    calculate_vacation_accrued_months,
)


def test_calculates_accrued_months_when_termination_month_has_fifteen_days() -> None:
    result = calculate_thirteenth_accrued_months(
        admission_date=date(2026, 1, 10),
        termination_date=date(2026, 8, 15),
    )

    assert result == 8


def test_does_not_count_termination_month_with_less_than_fifteen_days() -> None:
    result = calculate_thirteenth_accrued_months(
        admission_date=date(2026, 1, 10),
        termination_date=date(2026, 8, 14),
    )

    assert result == 7


def test_counts_admission_month_when_at_least_fifteen_days_are_worked() -> None:
    result = calculate_thirteenth_accrued_months(
        admission_date=date(2026, 1, 17),
        termination_date=date(2026, 3, 31),
    )

    assert result == 3


def test_does_not_count_admission_month_with_less_than_fifteen_days() -> None:
    result = calculate_thirteenth_accrued_months(
        admission_date=date(2026, 1, 18),
        termination_date=date(2026, 3, 31),
    )

    assert result == 2


def test_employee_admitted_before_termination_year_starts_from_january() -> None:
    result = calculate_thirteenth_accrued_months(
        admission_date=date(2024, 5, 10),
        termination_date=date(2026, 8, 20),
    )

    assert result == 8


def test_rejects_termination_before_admission() -> None:
    with pytest.raises(ValueError):
        calculate_thirteenth_accrued_months(
            admission_date=date(2026, 8, 20),
            termination_date=date(2026, 1, 10),
        )

def test_calculates_current_vacation_period_start() -> None:
    result = calculate_current_vacation_period_start(
        admission_date=date(2024, 1, 10),
        reference_date=date(2026, 8, 20),
    )

    assert result == date(2026, 1, 10)


def test_calculates_vacation_accrued_months() -> None:
    result = calculate_vacation_accrued_months(
        admission_date=date(2026, 1, 10),
        termination_date=date(2026, 7, 9),
    )

    assert result == 6


def test_counts_vacation_partial_month_with_fifteen_days() -> None:
    result = calculate_vacation_accrued_months(
        admission_date=date(2026, 1, 10),
        termination_date=date(2026, 7, 24),
    )

    assert result == 7


def test_does_not_count_vacation_partial_month_with_fourteen_days() -> None:
    result = calculate_vacation_accrued_months(
        admission_date=date(2026, 1, 10),
        termination_date=date(2026, 7, 23),
    )

    assert result == 6


def test_vacation_accrual_uses_current_accrual_period() -> None:
    result = calculate_vacation_accrued_months(
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
    )

    assert result == 7


def test_vacation_accrual_rejects_termination_before_admission() -> None:
    with pytest.raises(ValueError):
        calculate_vacation_accrued_months(
            admission_date=date(2026, 8, 20),
            termination_date=date(2026, 1, 10),
        )