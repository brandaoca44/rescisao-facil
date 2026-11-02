from decimal import Decimal, ROUND_HALF_UP


SUPPORTED_IRRF_YEAR = 2026

MONEY_QUANTIZER = Decimal("0.01")

SIMPLIFIED_MONTHLY_DEDUCTION_2026 = Decimal("607.20")

FULL_REDUCTION_LIMIT_2026 = Decimal("5000.00")
PARTIAL_REDUCTION_LIMIT_2026 = Decimal("7350.00")

PARTIAL_REDUCTION_BASE_2026 = Decimal("978.62")
PARTIAL_REDUCTION_FACTOR_2026 = Decimal("0.133145")


IRRF_BRACKETS_2026 = (
    (
        Decimal("2428.80"),
        Decimal("0.00"),
        Decimal("0.00"),
    ),
    (
        Decimal("2826.65"),
        Decimal("0.075"),
        Decimal("182.16"),
    ),
    (
        Decimal("3751.05"),
        Decimal("0.15"),
        Decimal("394.16"),
    ),
    (
        Decimal("4664.68"),
        Decimal("0.225"),
        Decimal("675.49"),
    ),
)


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def _calculate_progressive_irrf(
    calculation_base: Decimal,
) -> Decimal:
    """Aplica a tabela progressiva mensal do IRRF de 2026."""

    if calculation_base <= Decimal("0.00"):
        return Decimal("0.00")

    for limit, rate, deduction in IRRF_BRACKETS_2026:
        if calculation_base <= limit:
            tax = calculation_base * rate - deduction

            return _round_money(
                max(tax, Decimal("0.00"))
            )

    tax = (
        calculation_base * Decimal("0.275")
        - Decimal("908.73")
    )

    return _round_money(
        max(tax, Decimal("0.00"))
    )


def _calculate_irrf_reduction(
    taxable_income: Decimal,
    calculated_tax: Decimal,
) -> Decimal:
    """Calcula a redução do IRRF prevista para rendimentos de 2026."""

    if taxable_income <= FULL_REDUCTION_LIMIT_2026:
        return calculated_tax

    if taxable_income <= PARTIAL_REDUCTION_LIMIT_2026:
        reduction = (
            PARTIAL_REDUCTION_BASE_2026
            - (
                PARTIAL_REDUCTION_FACTOR_2026
                * taxable_income
            )
        )

        reduction = _round_money(
            max(reduction, Decimal("0.00"))
        )

        return min(reduction, calculated_tax)

    return Decimal("0.00")


def calculate_irrf(
    taxable_income: Decimal,
    inss_deduction: Decimal,
    year: int,
) -> Decimal:
    """Calcula o IRRF considerando a regra simplificada da V1."""

    if taxable_income < 0:
        raise ValueError(
            "IRRF taxable income cannot be negative."
        )

    if inss_deduction < 0:
        raise ValueError(
            "INSS deduction cannot be negative."
        )

    if year != SUPPORTED_IRRF_YEAR:
        raise NotImplementedError(
            f"IRRF table for {year} is not supported."
        )

    deduction = max(
        inss_deduction,
        SIMPLIFIED_MONTHLY_DEDUCTION_2026,
    )

    calculation_base = max(
        taxable_income - deduction,
        Decimal("0.00"),
    )

    calculated_tax = _calculate_progressive_irrf(
        calculation_base=calculation_base,
    )

    reduction = _calculate_irrf_reduction(
        taxable_income=taxable_income,
        calculated_tax=calculated_tax,
    )

    final_tax = calculated_tax - reduction

    return _round_money(
        max(final_tax, Decimal("0.00"))
    )


def calculate_termination_irrf(
    salary_balance: Decimal,
    salary_balance_inss: Decimal,
    thirteenth_salary: Decimal,
    thirteenth_inss: Decimal,
    year: int,
) -> tuple[Decimal, Decimal, Decimal]:
    """Calcula separadamente o IRRF mensal e o IRRF do 13º."""

    values = (
        salary_balance,
        salary_balance_inss,
        thirteenth_salary,
        thirteenth_inss,
    )

    if any(value < 0 for value in values):
        raise ValueError(
            "Termination IRRF values cannot be negative."
        )

    monthly_irrf = calculate_irrf(
        taxable_income=salary_balance,
        inss_deduction=salary_balance_inss,
        year=year,
    )

    thirteenth_irrf = calculate_irrf(
        taxable_income=thirteenth_salary,
        inss_deduction=thirteenth_inss,
        year=year,
    )

    total_irrf = monthly_irrf + thirteenth_irrf

    return (
        monthly_irrf,
        thirteenth_irrf,
        total_irrf,
    )