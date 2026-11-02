from decimal import Decimal

import pytest

from app.domain.termination_rules import get_termination_rules
from app.domain.termination_type import TerminationType


def test_without_cause_rules() -> None:
    rules = get_termination_rules(
        TerminationType.DISMISSAL_WITHOUT_CAUSE
    )

    assert rules.notice_pay_factor == Decimal("1.00")
    assert rules.pays_proportional_thirteenth is True
    assert rules.pays_proportional_vacation is True
    assert rules.fgts_penalty_rate == Decimal("0.40")


def test_resignation_rules() -> None:
    rules = get_termination_rules(
        TerminationType.RESIGNATION
    )

    assert rules.notice_pay_factor == Decimal("0.00")
    assert rules.pays_proportional_thirteenth is True
    assert rules.pays_proportional_vacation is True
    assert rules.fgts_penalty_rate == Decimal("0.00")


def test_mutual_agreement_rules() -> None:
    rules = get_termination_rules(
        TerminationType.MUTUAL_AGREEMENT
    )

    assert rules.notice_pay_factor == Decimal("0.50")
    assert rules.pays_proportional_thirteenth is True
    assert rules.pays_proportional_vacation is True
    assert rules.fgts_penalty_rate == Decimal("0.20")


def test_dismissal_with_cause_rules() -> None:
    rules = get_termination_rules(
        TerminationType.DISMISSAL_WITH_CAUSE
    )

    assert rules.notice_pay_factor == Decimal("0.00")
    assert rules.pays_proportional_thirteenth is False
    assert rules.pays_proportional_vacation is False
    assert rules.pays_acquired_vacation is True
    assert rules.pays_overdue_vacation is True
    assert rules.fgts_penalty_rate == Decimal("0.00")


@pytest.mark.parametrize(
    "termination_type",
    list(TerminationType),
)
def test_all_termination_types_have_rules(
    termination_type: TerminationType,
) -> None:
    rules = get_termination_rules(termination_type)

    assert rules is not None