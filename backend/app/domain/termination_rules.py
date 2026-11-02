from dataclasses import dataclass
from decimal import Decimal

from app.domain.termination_type import TerminationType


@dataclass(frozen=True)
class TerminationRules:
    """Define quais direitos são aplicáveis a uma modalidade de rescisão."""

    notice_pay_factor: Decimal
    pays_proportional_thirteenth: bool
    pays_proportional_vacation: bool
    pays_acquired_vacation: bool
    pays_overdue_vacation: bool
    fgts_penalty_rate: Decimal


TERMINATION_RULES = {
    TerminationType.DISMISSAL_WITHOUT_CAUSE: TerminationRules(
        notice_pay_factor=Decimal("1.00"),
        pays_proportional_thirteenth=True,
        pays_proportional_vacation=True,
        pays_acquired_vacation=True,
        pays_overdue_vacation=True,
        fgts_penalty_rate=Decimal("0.40"),
    ),

    TerminationType.RESIGNATION: TerminationRules(
        notice_pay_factor=Decimal("0.00"),
        pays_proportional_thirteenth=True,
        pays_proportional_vacation=True,
        pays_acquired_vacation=True,
        pays_overdue_vacation=True,
        fgts_penalty_rate=Decimal("0.00"),
    ),

    TerminationType.MUTUAL_AGREEMENT: TerminationRules(
        notice_pay_factor=Decimal("0.50"),
        pays_proportional_thirteenth=True,
        pays_proportional_vacation=True,
        pays_acquired_vacation=True,
        pays_overdue_vacation=True,
        fgts_penalty_rate=Decimal("0.20"),
    ),

    TerminationType.DISMISSAL_WITH_CAUSE: TerminationRules(
        notice_pay_factor=Decimal("0.00"),
        pays_proportional_thirteenth=False,
        pays_proportional_vacation=False,
        pays_acquired_vacation=True,
        pays_overdue_vacation=True,
        fgts_penalty_rate=Decimal("0.00"),
    ),
}


def get_termination_rules(
    termination_type: TerminationType,
) -> TerminationRules:
    """Retorna as regras aplicáveis à modalidade de rescisão."""

    try:
        return TERMINATION_RULES[termination_type]
    except KeyError as exc:
        raise NotImplementedError(
            f"Termination type '{termination_type}' is not supported."
        ) from exc