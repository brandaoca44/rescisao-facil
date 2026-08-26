from app.domain.accrual import (
    calculate_thirteenth_accrued_months,
    calculate_vacation_accrued_months,
)
from app.domain.fgts import (
    calculate_fgts_penalty,
    calculate_fgts_termination_deposit,
)
from app.domain.inss import calculate_termination_inss
from app.domain.notice_period import (
    calculate_notice_period_days,
    calculate_notice_period_value,
    calculate_projected_termination_date,
)
from app.domain.salary_balance import calculate_salary_balance
from app.domain.thirteenth_salary import (
    calculate_proportional_thirteenth_salary,
)
from app.domain.termination_type import TerminationType
from app.domain.vacation import (
    calculate_acquired_vacation,
    calculate_overdue_vacation,
    calculate_proportional_vacation,
    calculate_vacation_bonus,
)
from app.schemas.termination import (
    TerminationCalculationInput,
    TerminationCalculationResult,
)


def calculate_termination(
    data: TerminationCalculationInput,
) -> TerminationCalculationResult:
    """Orquestra o cálculo parcial da rescisão sem justa causa."""

    if data.termination_type != TerminationType.DISMISSAL_WITHOUT_CAUSE:
        raise NotImplementedError(
            "Only dismissal without cause is supported at this stage."
        )

    salary_balance = calculate_salary_balance(
        monthly_salary=data.monthly_salary,
        worked_days=data.termination_date.day,
    )

    notice_period_days = calculate_notice_period_days(
        admission_date=data.admission_date,
        termination_date=data.termination_date,
    )

    notice_period_value = calculate_notice_period_value(
        monthly_salary=data.monthly_salary,
        notice_period_days=notice_period_days,
    )

    projected_termination_date = calculate_projected_termination_date(
        termination_date=data.termination_date,
        notice_period_days=notice_period_days,
    )

    thirteenth_accrued_months = calculate_thirteenth_accrued_months(
        admission_date=data.admission_date,
        termination_date=projected_termination_date,
    )

    thirteenth_salary = calculate_proportional_thirteenth_salary(
        monthly_salary=data.monthly_salary,
        accrued_months=thirteenth_accrued_months,
    )

    vacation_accrued_months = calculate_vacation_accrued_months(
        admission_date=data.admission_date,
        termination_date=projected_termination_date,
    )

    proportional_vacation = calculate_proportional_vacation(
        monthly_salary=data.monthly_salary,
        accrued_months=vacation_accrued_months,
    )

    proportional_vacation_bonus = calculate_vacation_bonus(
        vacation_value=proportional_vacation,
    )

    acquired_vacation = calculate_acquired_vacation(
        monthly_salary=data.monthly_salary,
        periods=data.acquired_vacation_periods,
    )

    acquired_vacation_bonus = calculate_vacation_bonus(
        vacation_value=acquired_vacation,
    )

    overdue_vacation = calculate_overdue_vacation(
        monthly_salary=data.monthly_salary,
        periods=data.overdue_vacation_periods,
    )

    overdue_vacation_bonus = calculate_vacation_bonus(
        vacation_value=overdue_vacation,
    )

    fgts_termination_deposit = calculate_fgts_termination_deposit(
        salary_balance=salary_balance,
        thirteenth_salary=thirteenth_salary,
        notice_period_value=notice_period_value,
    )

    fgts_penalty = calculate_fgts_penalty(
        rescission_base=data.fgts_rescission_base,
    )

    inss_monthly, inss_thirteenth, inss_total = (
    calculate_termination_inss(
        salary_balance=salary_balance,
        thirteenth_salary=thirteenth_salary,
        year=data.termination_date.year,
    )
)

    total = (
        salary_balance
        + notice_period_value
        + thirteenth_salary
        + proportional_vacation
        + proportional_vacation_bonus
        + acquired_vacation
        + acquired_vacation_bonus
        + overdue_vacation
        + overdue_vacation_bonus
    )

    net_total = total - inss_total

    return TerminationCalculationResult(
        salary_balance=salary_balance,
        thirteenth_salary=thirteenth_salary,
        vacation_accrued_months=vacation_accrued_months,
        proportional_vacation=proportional_vacation,
        proportional_vacation_bonus=proportional_vacation_bonus,
        acquired_vacation=acquired_vacation,
        acquired_vacation_bonus=acquired_vacation_bonus,
        overdue_vacation=overdue_vacation,
        overdue_vacation_bonus=overdue_vacation_bonus,
        notice_period_days=notice_period_days,
        notice_period_value=notice_period_value,
        projected_termination_date=projected_termination_date,
        fgts_termination_deposit=fgts_termination_deposit,
        fgts_penalty=fgts_penalty,
        inss_monthly=inss_monthly,
        inss_thirteenth=inss_thirteenth,
        inss_total=inss_total,
        total=total,
        net_total=net_total,
    )