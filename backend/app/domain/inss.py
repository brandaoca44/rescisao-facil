from decimal import Decimal, ROUND_HALF_UP


SUPPORTED_INSS_YEAR = 2026
MONEY_QUANTIZER = Decimal("0.01")

INSS_BRACKETS_2026 = (
    (Decimal("1621.00"), Decimal("0.075")),
    (Decimal("2902.84"), Decimal("0.09")),
    (Decimal("4354.27"), Decimal("0.12")),
    (Decimal("8475.55"), Decimal("0.14")),
)


def calculate_inss_contribution(
    calculation_base: Decimal,
    year: int,
) -> Decimal:
    """Calcula a contribuição progressiva do INSS para empregado."""

    if calculation_base < 0:
        raise ValueError("INSS calculation base cannot be negative.")

    if year != SUPPORTED_INSS_YEAR:
        raise NotImplementedError(
            f"INSS contribution table for {year} is not supported."
        )

    contribution = Decimal("0.00")
    previous_limit = Decimal("0.00")

    capped_base = min(
        calculation_base,
        INSS_BRACKETS_2026[-1][0],
    )

    for bracket_limit, rate in INSS_BRACKETS_2026:
        if capped_base <= previous_limit:
            break

        taxable_amount = (
            min(capped_base, bracket_limit)
            - previous_limit
        )

        contribution += taxable_amount * rate
        previous_limit = bracket_limit

    return contribution.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def calculate_termination_inss(
    salary_balance: Decimal,
    thirteenth_salary: Decimal,
    year: int,
) -> tuple[Decimal, Decimal, Decimal]:
    """Calcula separadamente o INSS mensal e o INSS sobre o 13º."""

    if salary_balance < 0 or thirteenth_salary < 0:
        raise ValueError("Termination amounts cannot be negative.")

    monthly_inss = calculate_inss_contribution(
        calculation_base=salary_balance,
        year=year,
    )

    thirteenth_inss = calculate_inss_contribution(
        calculation_base=thirteenth_salary,
        year=year,
    )

    total_inss = monthly_inss + thirteenth_inss

    return (
        monthly_inss,
        thirteenth_inss,
        total_inss,
    )