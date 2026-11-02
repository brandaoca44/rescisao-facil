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

    model_config = ConfigDict(extra="forbid")

    monthly_salary: Decimal = Field(
        gt=0, max_digits=12, decimal_places=2, allow_inf_nan=False,
        description="Salário mensal bruto em reais, com até duas casas decimais.",
        examples=["3000.00"],
    )

    admission_date: date = Field(
        description="Data de admissão no formato AAAA-MM-DD.",
        examples=["2024-01-10"],
    )
    termination_date: date = Field(
        description=(
            "Data do desligamento efetivo antes da projeção indenizada. "
            "No aviso trabalhado, informar o último dia de cumprimento. "
            "As tabelas tributárias disponíveis atendem desligamentos em 2026."
        ),
        examples=["2026-08-20"],
    )

    termination_type: TerminationType = Field(
        description="Modalidade do desligamento; define as verbas aplicáveis.",
    )

    notice_period_type: NoticePeriodType | None = Field(
        default=None,
        description=(
            "Situação do aviso compatível com a modalidade. Omitido ou null "
            "preserva o comportamento anterior: indenizado na dispensa sem "
            "justa causa e no acordo; sem desconto no pedido de demissão; "
            "sem aviso na justa causa."
        ),
    )

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
        description="Base informada para a multa do FGTS; não é saldo disponível para saque.",
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

    gross_paid: Decimal = Field(description='Décimo terceiro bruto já pago informado, abatido uma vez no líquido.')
    gross_balance: Decimal = Field(description='Saldo bruto do décimo terceiro após o pagamento anterior.')
    inss_assessed: Decimal = Field(description='INSS integral apurado sobre o décimo terceiro, antes dos abatimentos.')
    irrf_assessed: Decimal = Field(description='IRRF integral apurado sobre o décimo terceiro, antes dos abatimentos.')
    inss_previously_withheld: Decimal = Field(description='INSS anterior informado e compensado no desconto atual.')
    irrf_previously_withheld: Decimal = Field(description='IRRF anterior informado e compensado no desconto atual.')
    fgts_previously_deposited: Decimal = Field(description='FGTS anterior informado e abatido do depósito rescisório.')


class TerminationCalculationResult(BaseModel):
    """Resultado das verbas atualmente suportadas pelo motor."""

    salary_balance: Decimal = Field(description='Saldo de salário bruto em reais.')

    thirteenth_salary: Decimal = Field(description='Décimo terceiro bruto integral, antes do pagamento anterior informado.')
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

    vacation_accrued_months: int = Field(description="Avos proporcionais do período aquisitivo incompleto.")
    proportional_vacation: Decimal = Field(description='Férias proporcionais do período incompleto, sem o adicional.')
    proportional_vacation_bonus: Decimal = Field(description='Adicional de um terço sobre as férias proporcionais.')

    acquired_vacation: Decimal = Field(description='Férias integrais simples informadas, sem o adicional.')
    acquired_vacation_bonus: Decimal = Field(description='Adicional de um terço sobre as férias adquiridas.')

    overdue_vacation: Decimal = Field(description='Férias integrais vencidas informadas, com a dobra e sem o adicional.')
    overdue_vacation_bonus: Decimal = Field(description='Adicional de um terço sobre o valor dobrado das férias vencidas.')

    notice_period_days: int = Field(description="Dias de aviso aplicáveis ao cenário, mesmo quando não há indenização.")
    notice_period_value: Decimal = Field(description='Aviso indenizado recebido; não representa desconto.')
    notice_period_discount: Decimal = Field(description='Desconto do aviso não cumprido no pedido de demissão.')
    projected_termination_date: date = Field(description="Fim da projeção indenizada; sem projeção, coincide com termination_date.")

    fgts_termination_deposit: Decimal = Field(description='Depósito das verbas calculadas, menos FGTS anterior do décimo terceiro informado. Fora de total e net_total.')
    fgts_penalty: Decimal = Field(description='Multa calculada sobre fgts_rescission_base; fora de total e net_total.')

    inss_monthly: Decimal = Field(description='INSS sobre o saldo salarial, separado do décimo terceiro.')
    inss_thirteenth: Decimal = Field(description='INSS adicional sobre o décimo terceiro, após a retenção anterior informada.')
    inss_total: Decimal = Field(description='Soma do INSS mensal com o adicional do décimo terceiro a descontar agora.')

    irrf_monthly: Decimal = Field(description='IRRF sobre o saldo salarial, com a dispensa de retenção mensal aplicável.')
    irrf_thirteenth: Decimal = Field(description='IRRF adicional sobre o décimo terceiro, após a retenção anterior informada.')
    irrf_total: Decimal = Field(description='Soma do IRRF mensal com o adicional do décimo terceiro a descontar agora.')

    total: Decimal = Field(description='Bruto integral das verbas, incluindo o décimo terceiro antes de pagamentos anteriores. Não inclui FGTS nem multa.')
    net_total: Decimal = Field(description='Bruto menos INSS, IRRF, desconto do aviso e décimo terceiro bruto já pago informado. Pode ser negativo se os descontos superarem as verbas.')

    benefits: TerminationBenefitsResult = Field(
        description="Direitos por modalidade, condicionados à sistemática de saque e aos requisitos individuais.",
    )
