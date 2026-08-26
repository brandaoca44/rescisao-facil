from decimal import Decimal, ROUND_HALF_UP


FGTS_RATE = Decimal("0.08")
DISMISSAL_WITHOUT_CAUSE_PENALTY_RATE = Decimal("0.40")
MONEY_QUANTIZER = Decimal("0.01")


def calculate_fgts_deposit(
    calculation_base: Decimal,
) -> Decimal:
    """Calcula o depósito de FGTS sobre uma base remuneratória."""

    if calculation_base < 0:
        raise ValueError("FGTS calculation base cannot be negative.")

    fgts_value = calculation_base * FGTS_RATE

    return fgts_value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def calculate_fgts_termination_deposit(
    salary_balance: Decimal,
    thirteenth_salary: Decimal,
    notice_period_value: Decimal,
) -> Decimal:
    """Calcula o FGTS incidente sobre as verbas rescisórias suportadas."""

    values = (
        salary_balance,
        thirteenth_salary,
        notice_period_value,
    )

    if any(value < 0 for value in values):
        raise ValueError("Termination amounts cannot be negative.")

    calculation_base = sum(values, Decimal("0.00"))

    return calculate_fgts_deposit(calculation_base)


def calculate_fgts_penalty(
    rescission_base: Decimal,
) -> Decimal:
    """Calcula a multa de 40% do FGTS na dispensa sem justa causa."""

    if rescission_base < 0:
        raise ValueError("FGTS rescission base cannot be negative.")

    penalty = rescission_base * DISMISSAL_WITHOUT_CAUSE_PENALTY_RATE

    return penalty.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )