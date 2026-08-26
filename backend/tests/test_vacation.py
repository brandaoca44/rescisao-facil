from decimal import Decimal

import pytest

from app.domain.vacation import (
    calculate_acquired_vacation,
    calculate_overdue_vacation,
    calculate_proportional_vacation,
    calculate_proportional_vacation_with_bonus,
    calculate_vacation_bonus,
)


@pytest.mark.parametrize(
    ("accrued_months", "expected"),
    [
        (0, Decimal("0.00")),
        (1, Decimal("250.00")),
        (6, Decimal("1500.00")),
        (12, Decimal("3000.00")),
    ],
)
def test_calculate_proportional_vacation(
    accrued_months: int,
    expected: Decimal,
) -> None:
    result = calculate_proportional_vacation(
        monthly_salary=Decimal("3000.00"),
        accrued_months=accrued_months,
    )

    assert result == expected


def test_calculate_vacation_bonus() -> None:
    result = calculate_vacation_bonus(
        vacation_value=Decimal("1500.00"),
    )

    assert result == Decimal("500.00")


def test_calculate_proportional_vacation_with_bonus() -> None:
    result = calculate_proportional_vacation_with_bonus(
        monthly_salary=Decimal("3000.00"),
        accrued_months=6,
    )

    assert result == Decimal("2000.00")


def test_rejects_negative_salary() -> None:
    with pytest.raises(ValueError):
        calculate_proportional_vacation(
            monthly_salary=Decimal("-3000.00"),
            accrued_months=6,
        )


@pytest.mark.parametrize("accrued_months", [-1, 13])
def test_rejects_invalid_accrued_months(
    accrued_months: int,
) -> None:
    with pytest.raises(ValueError):
        calculate_proportional_vacation(
            monthly_salary=Decimal("3000.00"),
            accrued_months=accrued_months,
        )


def test_vacation_bonus_rejects_negative_value() -> None:
    with pytest.raises(ValueError):
        calculate_vacation_bonus(
            vacation_value=Decimal("-100.00"),
        )

def test_calculate_acquired_vacation() -> None:
    result = calculate_acquired_vacation(
        monthly_salary=Decimal("3000.00"),
        periods=1,
    )

    assert result == Decimal("3000.00")


def test_calculate_multiple_acquired_vacation_periods() -> None:
    result = calculate_acquired_vacation(
        monthly_salary=Decimal("3000.00"),
        periods=2,
    )

    assert result == Decimal("6000.00")


def test_calculate_overdue_vacation() -> None:
    result = calculate_overdue_vacation(
        monthly_salary=Decimal("3000.00"),
        periods=1,
    )

    assert result == Decimal("6000.00")


def test_acquired_vacation_rejects_negative_periods() -> None:
    with pytest.raises(ValueError):
        calculate_acquired_vacation(
            monthly_salary=Decimal("3000.00"),
            periods=-1,
        )


def test_overdue_vacation_rejects_negative_periods() -> None:
    with pytest.raises(ValueError):
        calculate_overdue_vacation(
            monthly_salary=Decimal("3000.00"),
            periods=-1,
        )