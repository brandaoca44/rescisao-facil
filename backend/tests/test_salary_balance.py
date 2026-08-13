from decimal import Decimal

import pytest

from app.domain.salary_balance import calculate_salary_balance


def test_calculate_salary_balance_for_ten_worked_days() -> None:
    result = calculate_salary_balance(
        monthly_salary=Decimal("3000.00"),
        worked_days=10,
    )

    assert result == Decimal("1000.00")


def test_calculate_salary_balance_for_twenty_worked_days() -> None:
    result = calculate_salary_balance(
        monthly_salary=Decimal("3000.00"),
        worked_days=20,
    )

    assert result == Decimal("2000.00")


def test_calculate_salary_balance_with_zero_worked_days() -> None:
    result = calculate_salary_balance(
        monthly_salary=Decimal("3000.00"),
        worked_days=0,
    )

    assert result == Decimal("0.00")


def test_calculate_salary_balance_rejects_negative_salary() -> None:
    with pytest.raises(ValueError):
        calculate_salary_balance(
            monthly_salary=Decimal("-3000.00"),
            worked_days=10,
        )


@pytest.mark.parametrize("worked_days", [-1, 31])
def test_calculate_salary_balance_rejects_invalid_worked_days(
    worked_days: int,
) -> None:
    with pytest.raises(ValueError):
        calculate_salary_balance(
            monthly_salary=Decimal("3000.00"),
            worked_days=worked_days,
        )