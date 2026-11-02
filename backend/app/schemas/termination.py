from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field
from app.domain.notice_period_type import NoticePeriodType

from app.domain.termination_type import TerminationType


class ThirteenthPreviousPaymentInput(BaseModel):
    """Histórico de 13º exclusivamente do ano do desligamento, em valores brutos."""

    model_config = ConfigDict(extra="forbid")

    gross_amount: Decimal = Field(
        default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2,
        allow_inf_nan=False,
        description="Total bruto já pago ou adiantado, antes das retenções.",
    )
    inss_withheld: Decimal = Field(
        default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2,
        allow_inf_nan=False,
        description="INSS do empregado já descontado desse décimo terceiro.",
    )
    irrf_withheld: Decimal = Field(
        default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2,
        allow_inf_nan=False,
        description="IRRF já retido sobre esse décimo terceiro.",
    )
    fgts_deposited: Decimal = Field(
        default=Decimal("0.00"), ge=0, max_digits=12, decimal_places=2,
        allow_inf_nan=False,
        description="FGTS já depositado exclusivamente sobre esse décimo terceiro.",
    )


class TerminationCalculationInput(BaseModel):
    """Dados necessários para o cálculo da rescisão."""

    monthly_salary: Decimal = Field(gt=0, max_digits=12, decimal_places=2, allow_inf_nan=False)

    admission_date: date
    termination_date: date

    termination_type: TerminationType

    notice_period_type: NoticePeriodType | None = None

    acquired_vacation_periods: int = Field(
        default=0, ge=0,
        description=(
            "Períodos completos não quitados, ainda no prazo concessivo, "
            "na data projetada do desligamento. Incluir os completados "
            "pela projeção do aviso; não repetir em overdue_vacation_periods."
        ),
    )

    overdue_vacation_periods: int = Field(
        default=0, ge=0,
        description=(
            "Períodos integrais não quitados com prazo concessivo encerrado "
            "na data projetada, para pagamento em dobro. Não incluir "
            "períodos já gozados ou informados como férias adquiridas."
        ),
    )

    fgts_rescission_base: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        allow_inf_nan=False,
    )

    thirteenth_previous_payment: ThirteenthPreviousPaymentInput = Field(
        default_factory=ThirteenthPreviousPaymentInput,
        description=(
            "Pagamentos e retenções do décimo terceiro do ano do desligamento. "
            "Não incluir anos anteriores ou o ano futuro da projeção. "
            "Omitir significa valores anteriores iguais a zero."
        ),
    )


class TerminationBenefitsResult(BaseModel):
    """Direitos informativos condicionados às regras e à situação individual."""

    fgts_withdrawal_rate_under_saque_rescisao: Decimal = Field(
        ge=0, le=1,
        description=(
            "Fração do saldo vinculada ao desligamento na sistemática "
            "saque-rescisão: 1.00, 0.80 ou 0.00. Não indica valor disponível "
            "nem aplica a sistemática saque-aniversário."
        ),
    )
    unemployment_insurance_possible_by_termination_type: bool = Field(
        description=(
            "Indica apenas se a modalidade permite, em princípio, solicitar "
            "seguro-desemprego. Não avalia os demais requisitos de concessão."
        ),
    )
    notes: list[str] = Field(
        description="Condições e limitações dos direitos informados.",
    )


class ThirteenthSalaryYearResult(BaseModel):
    """Parcela do décimo terceiro atribuída a um ano de aquisição."""

    year: int = Field(ge=1, le=9999)
    accrued_months: int = Field(ge=0, le=12)
    value: Decimal = Field(ge=0)


class ThirteenthSettlementResult(BaseModel):
    """Apuração integral e compensações do histórico informado."""

    gross_paid: Decimal
    gross_balance: Decimal
    inss_assessed: Decimal
    irrf_assessed: Decimal
    inss_previously_withheld: Decimal
    irrf_previously_withheld: Decimal
    fgts_previously_deposited: Decimal


class TerminationCalculationResult(BaseModel):
    """Resultado das verbas atualmente suportadas pelo motor."""

    salary_balance: Decimal

    thirteenth_salary: Decimal
    thirteenth_salary_by_year: list[ThirteenthSalaryYearResult] = Field(
        description=(
            "Avos e valores por ano, do ano do desligamento ao fim da projeção. "
            "A soma dos valores corresponde a thirteenth_salary, antes de "
            "abatimentos dos pagamentos anteriores informados. "
            "Não indica mudança da competência tributária."
        ),
    )

    thirteenth_settlement: ThirteenthSettlementResult = Field(
        description=(
            "Histórico compensado e saldo bruto de 13º. O bruto integral "
            "permanece em thirteenth_salary e total; gross_paid é abatido "
            "somente no líquido. inss_thirteenth e irrf_thirteenth são "
            "as retenções adicionais após os abatimentos."
        ),
    )

    vacation_accrued_months: int
    proportional_vacation: Decimal
    proportional_vacation_bonus: Decimal

    acquired_vacation: Decimal
    acquired_vacation_bonus: Decimal

    overdue_vacation: Decimal
    overdue_vacation_bonus: Decimal

    notice_period_days: int
    notice_period_value: Decimal
    notice_period_discount: Decimal
    projected_termination_date: date

    fgts_termination_deposit: Decimal
    fgts_penalty: Decimal

    inss_monthly: Decimal
    inss_thirteenth: Decimal
    inss_total: Decimal

    irrf_monthly: Decimal
    irrf_thirteenth: Decimal
    irrf_total: Decimal

    total: Decimal
    net_total: Decimal

    benefits: TerminationBenefitsResult
