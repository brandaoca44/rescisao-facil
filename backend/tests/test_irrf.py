from decimal import Decimal

import pytest

from app.domain.irrf import (
    calculate_irrf,
    calculate_termination_irrf,
)


def test_irrf_is_zero_for_income_below_2026_reduction_limit() -> None:
    result = calculate_irrf(
        taxable_income=Decimal("4000.00"),
        inss_deduction=Decimal("373.41"),
        year=2026,
    )

    assert result == Decimal("0.00")


def test_irrf_is_zero_for_income_at_five_thousand() -> None:
    result = calculate_irrf(
        taxable_income=Decimal("5000.00"),
        inss_deduction=Decimal("509.60"),
        year=2026,
    )

    assert result == Decimal("0.00")


def test_irrf_applies_partial_reduction() -> None:
    result = calculate_irrf(
        taxable_income=Decimal("6000.00"),
        inss_deduction=Decimal("649.60"),
        year=2026,
    )

    assert result == Decimal("382.88")


def test_irrf_without_reduction_above_limit() -> None:
    result = calculate_irrf(
        taxable_income=Decimal("7607.20"),
        inss_deduction=Decimal("0.00"),
        year=2026,
    )

    assert result == Decimal("1016.27")


def test_calculate_termination_irrf() -> None:
    monthly_irrf, thirteenth_irrf, total_irrf = (
        calculate_termination_irrf(
            salary_balance=Decimal("2000.00"),
            salary_balance_inss=Decimal("155.69"),
            thirteenth_salary=Decimal("2250.00"),
            thirteenth_inss=Decimal("178.19"),
            year=2026,
        )
    )

    assert monthly_irrf == Decimal("0.00")
    assert thirteenth_irrf == Decimal("0.00")
    assert total_irrf == Decimal("0.00")


def test_irrf_rejects_negative_income() -> None:
    with pytest.raises(ValueError):
        calculate_irrf(
            taxable_income=Decimal("-1.00"),
            inss_deduction=Decimal("0.00"),
            year=2026,
        )


def test_irrf_rejects_negative_inss_deduction() -> None:
    with pytest.raises(ValueError):
        calculate_irrf(
            taxable_income=Decimal("3000.00"),
            inss_deduction=Decimal("-1.00"),
            year=2026,
        )


def test_irrf_rejects_unsupported_year() -> None:
    with pytest.raises(NotImplementedError):
        calculate_irrf(
            taxable_income=Decimal("3000.00"),
            inss_deduction=Decimal("0.00"),
            year=2025,
        )