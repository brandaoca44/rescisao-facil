import pytest

from datetime import date
from decimal import Decimal

from app.domain.termination_type import TerminationType
from app.schemas.termination import TerminationCalculationInput
from app.services.termination_service import calculate_termination
from app.domain.notice_period_type import NoticePeriodType


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

    assert result.irrf_monthly == Decimal("0.00")
    assert result.irrf_thirteenth == Decimal("0.00")
    assert result.irrf_total == Decimal("0.00")

    assert result.total == Decimal("22850.00")
    assert result.net_total == Decimal("22516.12")


def test_calculate_resignation() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.RESIGNATION,
        acquired_vacation_periods=1,
        overdue_vacation_periods=1,
        fgts_rescission_base=Decimal("10000.00"),
    )

    result = calculate_termination(data)

    assert result.salary_balance == Decimal("2000.00")

    # O aviso omitido preserva o comportamento sem desconto.
    # O desconto exige a situação explícita NOT_WORKED.
    assert result.notice_period_days == 0
    assert result.notice_period_value == Decimal("0.00")
    assert result.projected_termination_date == date(2026, 8, 20)

    # Pedido de demissão mantém direito ao 13º proporcional.
    assert result.thirteenth_salary == Decimal("2000.00")

    # Sem projeção do aviso, o período atual soma 7 avos completos.
    # A fração de 10/08 a 20/08 possui apenas 11 dias e não gera
    # um novo avo de férias proporcionais.
    assert result.vacation_accrued_months == 7
    assert result.proportional_vacation == Decimal("1750.00")
    assert result.proportional_vacation_bonus == Decimal("583.33")

    assert result.acquired_vacation == Decimal("3000.00")
    assert result.acquired_vacation_bonus == Decimal("1000.00")

    assert result.overdue_vacation == Decimal("6000.00")
    assert result.overdue_vacation_bonus == Decimal("2000.00")

    assert result.fgts_penalty == Decimal("0.00")

    assert result.total == Decimal("18333.33")
    assert result.net_total == Decimal("18021.95")


def test_calculate_mutual_agreement() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.MUTUAL_AGREEMENT,
        acquired_vacation_periods=1,
        overdue_vacation_periods=1,
        fgts_rescission_base=Decimal("10000.00"),
    )

    result = calculate_termination(data)

    assert result.salary_balance == Decimal("2000.00")

    # O valor indenizado do aviso é reduzido pela metade.
    assert result.notice_period_days == 36
    assert result.notice_period_value == Decimal("1800.00")

    assert result.thirteenth_salary == Decimal("2250.00")

    assert result.proportional_vacation > Decimal("0.00")
    assert result.acquired_vacation == Decimal("3000.00")
    assert result.overdue_vacation == Decimal("6000.00")

    # No acordo, a indenização compensatória do FGTS é de 20%.
    assert result.fgts_penalty == Decimal("2000.00")

def test_rejects_invalid_notice_period_for_resignation() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.RESIGNATION,
        notice_period_type=NoticePeriodType.INDEMNIFIED,
    )

    with pytest.raises(ValueError):
        calculate_termination(data)


def test_rejects_notice_period_for_dismissal_with_cause() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.DISMISSAL_WITH_CAUSE,
        notice_period_type=NoticePeriodType.WORKED,
    )

    with pytest.raises(ValueError):
        calculate_termination(data)

def test_calculate_indemnified_notice_period() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.DISMISSAL_WITHOUT_CAUSE,
        notice_period_type=NoticePeriodType.INDEMNIFIED,
        acquired_vacation_periods=1,
        overdue_vacation_periods=1,
        fgts_rescission_base=Decimal("10000.00"),
    )

    result = calculate_termination(data)

    assert result.notice_period_days == 36
    assert result.notice_period_value == Decimal("3600.00")
    assert result.notice_period_discount == Decimal("0.00")
    assert result.projected_termination_date == date(2026, 9, 25)

def test_calculate_worked_notice_period_for_resignation() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.RESIGNATION,
        notice_period_type=NoticePeriodType.WORKED,
    )

    result = calculate_termination(data)

    assert result.notice_period_days == 30
    assert result.notice_period_value == Decimal("0.00")
    assert result.notice_period_discount == Decimal("0.00")
    assert result.projected_termination_date == date(2026, 8, 20)

def test_calculate_not_worked_notice_period_for_resignation() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.RESIGNATION,
        notice_period_type=NoticePeriodType.NOT_WORKED,
    )

    result = calculate_termination(data)

    assert result.notice_period_days == 30
    assert result.notice_period_value == Decimal("0.00")
    assert result.notice_period_discount == Decimal("3000.00")
    assert result.projected_termination_date == date(2026, 8, 20)

    assert result.net_total == (
        result.total
        - result.inss_total
        - result.irrf_total
        - result.notice_period_discount
    )

def test_calculate_dismissal_with_cause() -> None:
    data = TerminationCalculationInput(
        monthly_salary=Decimal("3000.00"),
        admission_date=date(2024, 1, 10),
        termination_date=date(2026, 8, 20),
        termination_type=TerminationType.DISMISSAL_WITH_CAUSE,
        acquired_vacation_periods=1,
        overdue_vacation_periods=1,
        fgts_rescission_base=Decimal("10000.00"),
    )

    result = calculate_termination(data)

    assert result.salary_balance == Decimal("2000.00")

    assert result.notice_period_days == 0
    assert result.notice_period_value == Decimal("0.00")
    assert result.projected_termination_date == date(2026, 8, 20)

    assert result.thirteenth_salary == Decimal("0.00")

    assert result.vacation_accrued_months == 0
    assert result.proportional_vacation == Decimal("0.00")
    assert result.proportional_vacation_bonus == Decimal("0.00")

    # Férias já adquiridas continuam devidas.
    assert result.acquired_vacation == Decimal("3000.00")
    assert result.acquired_vacation_bonus == Decimal("1000.00")

    assert result.overdue_vacation == Decimal("6000.00")
    assert result.overdue_vacation_bonus == Decimal("2000.00")

    assert result.fgts_penalty == Decimal("0.00")

    assert result.total == Decimal("14000.00")
