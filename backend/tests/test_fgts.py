from decimal import Decimal

import pytest

from app.domain.fgts import (
    calculate_fgts_deposit,
    calculate_fgts_penalty,
    calculate_fgts_termination_deposit,
)


def test_calculate_fgts_deposit() -> None:
    result = calculate_fgts_deposit(
        calculation_base=Decimal("3000.00"),
    )

    assert result == Decimal("240.00")


def test_calculate_fgts_termination_deposit() -> None:
    result = calculate_fgts_termination_deposit(
        salary_balance=Decimal("2000.00"),
        thirteenth_salary=Decimal("2250.00"),
        notice_period_value=Decimal("3600.00"),
    )

    assert result == Decimal("628.00")


def test_calculate_fgts_penalty_with_forty_percent_rate() -> None:
    result = calculate_fgts_penalty(
        rescission_base=Decimal("10000.00"),
        penalty_rate=Decimal("0.40"),
    )

    assert result == Decimal("4000.00")


def test_calculate_fgts_penalty_with_twenty_percent_rate() -> None:
    result = calculate_fgts_penalty(
        rescission_base=Decimal("10000.00"),
        penalty_rate=Decimal("0.20"),
    )

    assert result == Decimal("2000.00")


def test_calculate_fgts_penalty_with_zero_rate() -> None:
    result = calculate_fgts_penalty(
        rescission_base=Decimal("10000.00"),
        penalty_rate=Decimal("0.00"),
    )

    assert result == Decimal("0.00")


def test_calculate_fgts_penalty_with_zero_base() -> None:
    result = calculate_fgts_penalty(
        rescission_base=Decimal("0.00"),
        penalty_rate=Decimal("0.40"),
    )

    assert result == Decimal("0.00")


def test_fgts_deposit_rejects_negative_base() -> None:
    with pytest.raises(ValueError):
        calculate_fgts_deposit(
            calculation_base=Decimal("-100.00"),
        )


def test_fgts_penalty_rejects_negative_base() -> None:
    with pytest.raises(ValueError):
        calculate_fgts_penalty(
            rescission_base=Decimal("-100.00"),
            penalty_rate=Decimal("0.40"),
        )


def test_fgts_penalty_rejects_negative_rate() -> None:
    with pytest.raises(ValueError):
        calculate_fgts_penalty(
            rescission_base=Decimal("10000.00"),
            penalty_rate=Decimal("-0.01"),
        )


@pytest.mark.parametrize(
    ("salary_balance", "thirteenth_salary", "notice_period_value"),
    [
        (
            Decimal("-1.00"),
            Decimal("1000.00"),
            Decimal("1000.00"),
        ),
        (
            Decimal("1000.00"),
            Decimal("-1.00"),
            Decimal("1000.00"),
        ),
        (
            Decimal("1000.00"),
            Decimal("1000.00"),
            Decimal("-1.00"),
        ),
    ],
)
def test_fgts_termination_deposit_rejects_negative_amounts(
    salary_balance: Decimal,
    thirteenth_salary: Decimal,
    notice_period_value: Decimal,
) -> None:
    with pytest.raises(ValueError):
        calculate_fgts_termination_deposit(
            salary_balance=salary_balance,
            thirteenth_salary=thirteenth_salary,
            notice_period_value=notice_period_value,
        )