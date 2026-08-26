from datetime import date
from decimal import Decimal

import pytest

from app.domain.termination_type import TerminationType
from app.schemas.termination import TerminationCalculationInput
from app.services.termination_service import calculate_termination


def test_calculate_termination_without_cause() -> None:
    data = TerminationCalculationInput(
    monthly_salary=Decimal("3000.00"),
    admission_date=date(2024, 1, 10),
    termination_date=date(2026, 8, 20),
    termination_type=TerminationType.DISMISSAL_WITHOUT_CAUSE,
    acquired_vacation_periods=1,
    overdue_vacation_periods=1,
    fgts_rescission_base=Decimal("10000.00"),
)

    result = calculate_termination(data)

    assert result.salary_balance == Decimal("2000.00")

    assert result.notice_period_days == 36
    assert result.notice_period_value == Decimal("3600.00")
    assert result.projected_termination_date == date(2026, 9, 25)

    assert result.thirteenth_salary == Decimal("2250.00")

    assert result.vacation_accrued_months == 9
    assert result.proportional_vacation == Decimal("2250.00")
    assert result.proportional_vacation_bonus == Decimal("750.00")

    assert result.acquired_vacation == Decimal("3000.00")
    assert result.acquired_vacation_bonus == Decimal("1000.00")

    assert result.overdue_vacation == Decimal("6000.00")
    assert result.overdue_vacation_bonus == Decimal("2000.00")

    assert result.fgts_termination_deposit == Decimal("628.00")
    assert result.fgts_penalty == Decimal("4000.00")

    assert result.inss_monthly == Decimal("155.69")
    assert result.inss_thirteenth == Decimal("178.19")
    assert result.inss_total == Decimal("333.88")

    assert result.total == Decimal("22850.00")


@pytest.mark.parametrize(
    "termination_type",
    [
        TerminationType.RESIGNATION,
        TerminationType.MUTUAL_AGREEMENT,
        TerminationType.DISMISSAL_WITH_CAUSE,
    ],
)
def test_calculate_termination_rejects_unsupported_types(
    termination_type: TerminationType,
) -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=termination_type,
    )

    with pytest.raises(NotImplementedError):
        calculate_termination(data)