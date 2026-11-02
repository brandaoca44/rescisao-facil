from datetime import date
from decimal import Decimal

from app.domain.notice_period_type import NoticePeriodType
from app.domain.termination_type import TerminationType
from app.schemas.termination import TerminationCalculationInput


def test_termination_input_accepts_notice_period_type() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.DISMISSAL_WITHOUT_CAUSE,
        notice_period_type=NoticePeriodType.INDEMNIFIED,
    )

    assert data.notice_period_type == NoticePeriodType.INDEMNIFIED


def test_termination_input_keeps_notice_period_type_optional() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.DISMISSAL_WITHOUT_CAUSE,
    )

    assert data.notice_period_type is None