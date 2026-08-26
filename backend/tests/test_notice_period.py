from datetime import date

import pytest

from decimal import Decimal

from app.domain.notice_period import (
    calculate_notice_period_days,
    calculate_notice_period_value,
    calculate_projected_termination_date,
)


@pytest.mark.parametrize(
    ("admission_date", "termination_date", "expected_days"),
    [
        (
            date(2026, 1, 1),
            date(2026, 8, 1),
            30,
        ),
        (
            date(2025, 1, 1),
            date(2026, 1, 1),
            33,
        ),
        (
            date(2024, 1, 1),
            date(2026, 1, 1),
            36,
        ),
        (
            date(2021, 1, 1),
            date(2026, 1, 1),
            45,
        ),
        (
            date(2006, 1, 1),
            date(2026, 1, 1),
            90,
        ),
        (
            date(1996, 1, 1),
            date(2026, 1, 1),
            90,
        ),
    ],
)
def test_calculate_notice_period_days(
    admission_date: date,
    termination_date: date,
    expected_days: int,
) -> None:
    result = calculate_notice_period_days(
        admission_date=admission_date,
        termination_date=termination_date,
    )

    assert result == expected_days


def test_rejects_termination_before_admission() -> None:
    with pytest.raises(ValueError):
        calculate_notice_period_days(
            admission_date=date(2026, 8, 1),
            termination_date=date(2026, 1, 1),
        )

def test_calculates_projected_termination_date() -> None:
    result = calculate_projected_termination_date(
        termination_date=date(2026, 8, 1),
        notice_period_days=30,
    )

    assert result == date(2026, 8, 31)


def test_projected_termination_date_can_cross_month() -> None:
    result = calculate_projected_termination_date(
        termination_date=date(2026, 8, 20),
        notice_period_days=30,
    )

    assert result == date(2026, 9, 19)


def test_projected_termination_date_can_cross_year() -> None:
    result = calculate_projected_termination_date(
        termination_date=date(2026, 12, 20),
        notice_period_days=30,
    )

    assert result == date(2027, 1, 19)


def test_projected_termination_date_rejects_negative_notice() -> None:
    with pytest.raises(ValueError):
        calculate_projected_termination_date(
            termination_date=date(2026, 8, 20),
            notice_period_days=-1,
        )

def test_calculate_notice_period_value_for_thirty_days() -> None:
    result = calculate_notice_period_value(
        monthly_salary=Decimal("3000.00"),
        notice_period_days=30,
    )

    assert result == Decimal("3000.00")


def test_calculate_notice_period_value_for_thirty_six_days() -> None:
    result = calculate_notice_period_value(
        monthly_salary=Decimal("3000.00"),
        notice_period_days=36,
    )

    assert result == Decimal("3600.00")


def test_calculate_notice_period_value_for_ninety_days() -> None:
    result = calculate_notice_period_value(
        monthly_salary=Decimal("3000.00"),
        notice_period_days=90,
    )

    assert result == Decimal("9000.00")


def test_notice_period_value_rejects_negative_salary() -> None:
    with pytest.raises(ValueError):
        calculate_notice_period_value(
            monthly_salary=Decimal("-3000.00"),
            notice_period_days=30,
        )


def test_notice_period_value_rejects_negative_days() -> None:
    with pytest.raises(ValueError):
        calculate_notice_period_value(
            monthly_salary=Decimal("3000.00"),
            notice_period_days=-1,
        )