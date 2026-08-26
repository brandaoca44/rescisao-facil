from decimal import Decimal

import pytest

from app.domain.inss import (
    calculate_inss_contribution,
    calculate_termination_inss,
)


@pytest.mark.parametrize(
    ("calculation_base", "expected"),
    [
        (Decimal("0.00"), Decimal("0.00")),
        (Decimal("1621.00"), Decimal("121.58")),
        (Decimal("2000.00"), Decimal("155.69")),
        (Decimal("2250.00"), Decimal("178.19")),
        (Decimal("3000.00"), Decimal("248.60")),
        (Decimal("8475.55"), Decimal("988.09")),
        (Decimal("10000.00"), Decimal("988.09")),
    ],
)
def test_calculate_inss_contribution(
    calculation_base: Decimal,
    expected: Decimal,
) -> None:
    result = calculate_inss_contribution(
        calculation_base=calculation_base,
        year=2026,
    )

    assert result == expected


def test_calculate_termination_inss() -> None:
    monthly_inss, thirteenth_inss, total_inss = (
        calculate_termination_inss(
            salary_balance=Decimal("2000.00"),
            thirteenth_salary=Decimal("2250.00"),
            year=2026,
        )
    )

    assert monthly_inss == Decimal("155.69")
    assert thirteenth_inss == Decimal("178.19")
    assert total_inss == Decimal("333.88")


def test_inss_rejects_negative_base() -> None:
    with pytest.raises(ValueError):
        calculate_inss_contribution(
            calculation_base=Decimal("-1.00"),
            year=2026,
        )


def test_inss_rejects_unsupported_year() -> None:
    with pytest.raises(NotImplementedError):
        calculate_inss_contribution(
            calculation_base=Decimal("3000.00"),
            year=2025,
        )