from decimal import Decimal

import pytest

from app.domain.thirteenth_salary import (
    calculate_proportional_thirteenth_salary,
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
def test_calculate_proportional_thirteenth_salary(
    accrued_months: int,
    expected: Decimal,
) -> None:
    result = calculate_proportional_thirteenth_salary(
        monthly_salary=Decimal("3000.00"),
        accrued_months=accrued_months,
    )

    assert result == expected


def test_calculate_proportional_thirteenth_salary_rejects_negative_salary() -> None:
    with pytest.raises(ValueError):
        calculate_proportional_thirteenth_salary(
            monthly_salary=Decimal("-3000.00"),
            accrued_months=6,
        )


@pytest.mark.parametrize("accrued_months", [-1, 13])
def test_calculate_proportional_thirteenth_salary_rejects_invalid_months(
    accrued_months: int,
) -> None:
    with pytest.raises(ValueError):
        calculate_proportional_thirteenth_salary(
            monthly_salary=Decimal("3000.00"),
            accrued_months=accrued_months,
        )