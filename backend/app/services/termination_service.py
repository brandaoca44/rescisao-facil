from decimal import Decimal, ROUND_HALF_UP

from app.domain.accrual import (
    calculate_thirteenth_accrued_months,
    calculate_vacation_accrued_months,
)
from app.domain.fgts import (
    calculate_fgts_penalty,
    calculate_fgts_termination_deposit,
)
from app.domain.inss import SUPPORTED_INSS_YEAR, calculate_termination_inss
from app.domain.irrf import SUPPORTED_IRRF_YEAR, calculate_termination_irrf
from app.domain.notice_period import (
    calculate_notice_period_days,
    calculate_notice_period_value,
    calculate_projected_termination_date,
)
from app.domain.salary_balance import calculate_salary_balance_for_dates
from app.domain.thirteenth_salary import (
    calculate_proportional_thirteenth_salary,
)
from app.domain.termination_rules import get_termination_rules
from app.domain.termination_type import TerminationType
from app.domain.vacation import (
    calculate_acquired_vacation,
    calculate_overdue_vacation,
    calculate_proportional_vacation,
    calculate_vacation_bonus,
    validate_vacation_periods,
)
from app.domain.notice_period_rules import validate_notice_period_type
from app.domain.notice_period_type import NoticePeriodType

from app.schemas.termination import (
    TerminationCalculationInput,
    TerminationCalculationResult,
)


def calculate_termination(
    data: TerminationCalculationInput,
) -> TerminationCalculationResult:
    """Orquestra o cálculo da rescisão conforme a modalidade informada."""

    year = data.termination_date.year
    if year != SUPPORTED_INSS_YEAR or year != SUPPORTED_IRRF_YEAR:
        raise NotImplementedError(
            f"Termination calculation tables for {year} are not supported."
        )

    # Recupera as regras específicas do tipo de desligamento.
    rules = get_termination_rules(data.termination_type)

    validate_notice_period_type(
        termination_type=data.termination_type,
        notice_period_type=data.notice_period_type,
    )

    # Saldo de salário é devido independentemente da modalidade.
    salary_balance = calculate_salary_balance_for_dates(
        monthly_salary=data.monthly_salary,
        admission_date=data.admission_date,
        termination_date=data.termination_date,
    )

    # Calcula quantos dias de aviso correspondem ao tempo de serviço.
    base_notice_period_days = calculate_notice_period_days(
        admission_date=data.admission_date,
        termination_date=data.termination_date,
    )

    # No pedido de demissão, o aviso devido pelo trabalhador
    # permanece limitado a 30 dias.
    applicable_notice_period_days = (
        30
        if data.termination_type == TerminationType.RESIGNATION
        else base_notice_period_days
    )

    # Calcula o valor integral do aviso proporcional.
    full_notice_period_value = calculate_notice_period_value(
        monthly_salary=data.monthly_salary,
        notice_period_days=applicable_notice_period_days,
    )

    # Mantém o comportamento consolidado para chamadas antigas que ainda
    # não informam explicitamente a situação do aviso prévio.
    if data.notice_period_type is None:
        notice_period_days = (
            base_notice_period_days
            if rules.notice_pay_factor > Decimal("0.00")
            else 0
        )

        notice_period_value = (
            full_notice_period_value
            * rules.notice_pay_factor
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        notice_period_discount = Decimal("0.00")

        if rules.notice_pay_factor > Decimal("0.00"):
            projected_termination_date = (
                calculate_projected_termination_date(
                    termination_date=data.termination_date,
                    notice_period_days=base_notice_period_days,
                )
            )
        else:
            projected_termination_date = data.termination_date

    elif data.notice_period_type == NoticePeriodType.INDEMNIFIED:
        notice_period_days = base_notice_period_days

        notice_period_value = (
            full_notice_period_value
            * rules.notice_pay_factor
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        notice_period_discount = Decimal("0.00")

        projected_termination_date = (
            calculate_projected_termination_date(
                termination_date=data.termination_date,
                notice_period_days=base_notice_period_days,
            )
        )

    elif data.notice_period_type == NoticePeriodType.WORKED:
        notice_period_days = applicable_notice_period_days
        notice_period_value = Decimal("0.00")
        notice_period_discount = Decimal("0.00")
        projected_termination_date = data.termination_date

    else:
        # NOT_WORKED é válido nesta V1 para pedido de demissão.
        # O empregado não recebe aviso indenizado e o valor
        # correspondente é tratado separadamente como desconto.
        notice_period_days = applicable_notice_period_days
        notice_period_value = Decimal("0.00")
        notice_period_discount = full_notice_period_value
        projected_termination_date = data.termination_date

    validate_vacation_periods(
        admission_date=data.admission_date,
        reference_date=projected_termination_date,
        acquired_periods=data.acquired_vacation_periods,
        overdue_periods=data.overdue_vacation_periods,
    )

    # 13º proporcional.
    if rules.pays_proportional_thirteenth:
        thirteenth_accrued_months = (
            calculate_thirteenth_accrued_months(
                admission_date=data.admission_date,
                termination_date=projected_termination_date,
            )
        )

        thirteenth_salary = (
            calculate_proportional_thirteenth_salary(
                monthly_salary=data.monthly_salary,
                accrued_months=thirteenth_accrued_months,
            )
        )
    else:
        thirteenth_salary = Decimal("0.00")

    # Férias proporcionais.
    if rules.pays_proportional_vacation:
        vacation_accrued_months = (
            calculate_vacation_accrued_months(
                admission_date=data.admission_date,
                termination_date=projected_termination_date,
            )
        )

        proportional_vacation = (
            calculate_proportional_vacation(
                monthly_salary=data.monthly_salary,
                accrued_months=vacation_accrued_months,
            )
        )

        proportional_vacation_bonus = (
            calculate_vacation_bonus(
                vacation_value=proportional_vacation,
            )
        )
    else:
        vacation_accrued_months = 0
        proportional_vacation = Decimal("0.00")
        proportional_vacation_bonus = Decimal("0.00")

    # Férias adquiridas.
    if rules.pays_acquired_vacation:
        acquired_vacation = calculate_acquired_vacation(
            monthly_salary=data.monthly_salary,
            periods=data.acquired_vacation_periods,
        )

        acquired_vacation_bonus = calculate_vacation_bonus(
            vacation_value=acquired_vacation,
        )
    else:
        acquired_vacation = Decimal("0.00")
        acquired_vacation_bonus = Decimal("0.00")

    # Férias vencidas pagas em dobro.
    if rules.pays_overdue_vacation:
        overdue_vacation = calculate_overdue_vacation(
            monthly_salary=data.monthly_salary,
            periods=data.overdue_vacation_periods,
        )

        overdue_vacation_bonus = calculate_vacation_bonus(
            vacation_value=overdue_vacation,
        )
    else:
        overdue_vacation = Decimal("0.00")
        overdue_vacation_bonus = Decimal("0.00")

    # FGTS incidente sobre as verbas que efetivamente existem
    # para aquela modalidade.
    fgts_termination_deposit = (
        calculate_fgts_termination_deposit(
            salary_balance=salary_balance,
            thirteenth_salary=thirteenth_salary,
            notice_period_value=notice_period_value,
        )
    )

    # A multa utiliza o percentual definido pelas regras da modalidade.
    fgts_penalty = calculate_fgts_penalty(
        rescission_base=data.fgts_rescission_base,
        penalty_rate=rules.fgts_penalty_rate,
    )

    # INSS.
    inss_monthly, inss_thirteenth, inss_total = (
        calculate_termination_inss(
            salary_balance=salary_balance,
            thirteenth_salary=thirteenth_salary,
            year=data.termination_date.year,
        )
    )

    # IRRF.
    irrf_monthly, irrf_thirteenth, irrf_total = (
        calculate_termination_irrf(
            salary_balance=salary_balance,
            salary_balance_inss=inss_monthly,
            thirteenth_salary=thirteenth_salary,
            thirteenth_inss=inss_thirteenth,
            year=data.termination_date.year,
        )
    )

    # Total bruto pago diretamente ao trabalhador.
    #
    # FGTS e multa rescisória continuam fora deste total.
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

    # Total líquido após os descontos tributários implementados.
    net_total = (
        total
        - inss_total
        - irrf_total
        - notice_period_discount
    )

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
        notice_period_discount=notice_period_discount,
        projected_termination_date=projected_termination_date,
        fgts_termination_deposit=fgts_termination_deposit,
        fgts_penalty=fgts_penalty,
        inss_monthly=inss_monthly,
        inss_thirteenth=inss_thirteenth,
        inss_total=inss_total,
        irrf_monthly=irrf_monthly,
        irrf_thirteenth=irrf_thirteenth,
        irrf_total=irrf_total,
        total=total,
        net_total=net_total,
    )
