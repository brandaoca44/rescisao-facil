from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.termination_type import TerminationType


class TerminationCalculationInput(BaseModel):
    """Dados necessários para o cálculo da rescisão."""

    monthly_salary: Decimal = Field(gt=0)

    admission_date: date
    termination_date: date

    termination_type: TerminationType

    acquired_vacation_periods: int = Field(
        default=0,
        ge=0,
    )

    overdue_vacation_periods: int = Field(
        default=0,
        ge=0,
    )

    fgts_rescission_base: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )


class TerminationCalculationResult(BaseModel):
    """Resultado das verbas atualmente suportadas pelo motor."""

    salary_balance: Decimal

    thirteenth_salary: Decimal

    vacation_accrued_months: int
    proportional_vacation: Decimal
    proportional_vacation_bonus: Decimal

    acquired_vacation: Decimal
    acquired_vacation_bonus: Decimal

    overdue_vacation: Decimal
    overdue_vacation_bonus: Decimal

    notice_period_days: int
    notice_period_value: Decimal
    projected_termination_date: date

    fgts_termination_deposit: Decimal
    fgts_penalty: Decimal

    inss_monthly: Decimal
    inss_thirteenth: Decimal
    inss_total: Decimal

    total: Decimal
    net_total: Decimal