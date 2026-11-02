from decimal import Decimal

import pytest

from app.domain.termination_benefits import get_termination_benefits
from app.domain.termination_type import TerminationType


@pytest.mark.parametrize(("kind", "rate", "insurance"), [
    (TerminationType.DISMISSAL_WITHOUT_CAUSE, "1.00", True),
    (TerminationType.RESIGNATION, "0.00", False),
    (TerminationType.MUTUAL_AGREEMENT, "0.80", False),
    (TerminationType.DISMISSAL_WITH_CAUSE, "0.00", False),
])
def test_benefits_by_termination_type(kind, rate, insurance):
    benefits = get_termination_benefits(kind)
    assert benefits.fgts_withdrawal_rate_under_saque_rescisao == Decimal(rate)
    assert benefits.unemployment_insurance_possible_by_termination_type is insurance
    assert benefits.notes
    if rate != "0.00":
        assert any("saque-aniversário" in note for note in benefits.notes)
        assert any("não confirma saldo disponível" in note for note in benefits.notes)
    else:
        assert any("Outras hipóteses legais" in note for note in benefits.notes)
    if insurance:
        assert any("demais requisitos" in note for note in benefits.notes)


def test_rejects_unsupported_termination_type():
    with pytest.raises(NotImplementedError):
        get_termination_benefits("unsupported")
