from decimal import Decimal, ROUND_HALF_UP


MONTHS_IN_YEAR = Decimal("12")
MONEY_QUANTIZER = Decimal("0.01")


def calculate_proportional_thirteenth_salary(
    monthly_salary: Decimal,
    accrued_months: int,
) -> Decimal:
    """Calcula o 13º salário proporcional com base nos avos adquiridos."""

    if monthly_salary < 0:
        raise ValueError("Monthly salary cannot be negative.")

    if accrued_months < 0 or accrued_months > 12:
        raise ValueError("Accrued months must be between 0 and 12.")

    proportional_value = (
        monthly_salary / MONTHS_IN_YEAR
    ) * accrued_months

    return proportional_value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )