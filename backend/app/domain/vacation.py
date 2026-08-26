from decimal import Decimal, ROUND_HALF_UP


MONTHS_IN_ACCRUAL_PERIOD = Decimal("12")
CONSTITUTIONAL_VACATION_BONUS_DIVISOR = Decimal("3")
OVERDUE_VACATION_MULTIPLIER = Decimal("2")
MONEY_QUANTIZER = Decimal("0.01")


def calculate_proportional_vacation(
    monthly_salary: Decimal,
    accrued_months: int,
) -> Decimal:
    """Calcula o valor-base das férias proporcionais."""

    if monthly_salary < 0:
        raise ValueError("Monthly salary cannot be negative.")

    if accrued_months < 0 or accrued_months > 12:
        raise ValueError("Accrued months must be between 0 and 12.")

    proportional_vacation = (
        monthly_salary / MONTHS_IN_ACCRUAL_PERIOD
    ) * accrued_months

    return proportional_vacation.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def calculate_vacation_bonus(
    vacation_value: Decimal,
) -> Decimal:
    """Calcula o adicional constitucional de 1/3 sobre férias."""

    if vacation_value < 0:
        raise ValueError("Vacation value cannot be negative.")

    bonus = vacation_value / CONSTITUTIONAL_VACATION_BONUS_DIVISOR

    return bonus.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def calculate_proportional_vacation_with_bonus(
    monthly_salary: Decimal,
    accrued_months: int,
) -> Decimal:
    """Calcula férias proporcionais acrescidas do adicional de 1/3."""

    vacation_value = calculate_proportional_vacation(
        monthly_salary=monthly_salary,
        accrued_months=accrued_months,
    )

    vacation_bonus = calculate_vacation_bonus(vacation_value)

    return vacation_value + vacation_bonus


def calculate_acquired_vacation(
    monthly_salary: Decimal,
    periods: int,
) -> Decimal:
    """Calcula férias integrais adquiridas e ainda não gozadas."""

    if monthly_salary < 0:
        raise ValueError("Monthly salary cannot be negative.")

    if periods < 0:
        raise ValueError("Vacation periods cannot be negative.")

    vacation_value = monthly_salary * periods

    return vacation_value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )


def calculate_overdue_vacation(
    monthly_salary: Decimal,
    periods: int,
) -> Decimal:
    """Calcula férias vencidas sujeitas ao pagamento em dobro."""

    if monthly_salary < 0:
        raise ValueError("Monthly salary cannot be negative.")

    if periods < 0:
        raise ValueError("Vacation periods cannot be negative.")

    vacation_value = (
        monthly_salary
        * OVERDUE_VACATION_MULTIPLIER
        * periods
    )

    return vacation_value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )