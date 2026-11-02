from decimal import Decimal

import pytest

from app.domain.thirteenth_salary import (
    ThirteenthPreviousPayment, settle_thirteenth_salary,
)


def settle(**changes):
    arguments = dict(
        gross_amount=Decimal("3250.00"), current_year_amount=Decimal("3000.00"),
        inss_assessed=Decimal("278.60"), irrf_assessed=Decimal("0.00"),
        current_year_fgts=Decimal("240.00"), previous=ThirteenthPreviousPayment(),
    )
    return settle_thirteenth_salary(**{**arguments, **changes})


def test_compensates_previous_gross_and_retention_without_reducing_tax_base():
    result = settle(previous=ThirteenthPreviousPayment(
        gross_amount=Decimal("3000.00"), inss_withheld=Decimal("248.60"),
        fgts_deposited=Decimal("240.00"),
    ))
    assert result.gross_balance == Decimal("250.00")
    assert result.inss_remaining == Decimal("30.00")
    assert result.irrf_remaining == Decimal("0.00")


def test_plain_advance_does_not_reduce_tax_to_be_withheld():
    result = settle(previous=ThirteenthPreviousPayment(gross_amount=Decimal("1500.00")))
    assert result.gross_balance == Decimal("1750.00")
    assert result.inss_remaining == Decimal("278.60")


@pytest.mark.parametrize("previous", [
    ThirteenthPreviousPayment(gross_amount=Decimal("3000.01")),
    ThirteenthPreviousPayment(inss_withheld=Decimal("1.00")),
    ThirteenthPreviousPayment(fgts_deposited=Decimal("1.00")),
    ThirteenthPreviousPayment(gross_amount=Decimal("3000.00"), inss_withheld=Decimal("278.61")),
    ThirteenthPreviousPayment(gross_amount=Decimal("3000.00"), irrf_withheld=Decimal("0.01")),
    ThirteenthPreviousPayment(gross_amount=Decimal("3000.00"), fgts_deposited=Decimal("240.01")),
    ThirteenthPreviousPayment(gross_amount=Decimal("NaN")),
    ThirteenthPreviousPayment(gross_amount=Decimal("-1.00")),
])
def test_rejects_inconsistent_history_and_unsupported_recoveries(previous):
    with pytest.raises(ValueError):
        settle(previous=previous)
