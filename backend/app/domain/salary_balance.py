from decimal import Decimal, ROUND_HALF_UP


DAYS_IN_MONTH_FOR_SALARY_CALCULATION = Decimal("30")
MONEY_QUANTIZER = Decimal("0.01")


def calculate_salary_balance(
    monthly_salary: Decimal,
    worked_days: int,
) -> Decimal:
    """Calcula o saldo de salário devido no mês da rescisão."""

    if monthly_salary < 0:
        raise ValueError("Monthly salary cannot be negative.")

    if worked_days < 0 or worked_days > 30:
        raise ValueError("Worked days must be between 0 and 30.")

    daily_salary = monthly_salary / DAYS_IN_MONTH_FOR_SALARY_CALCULATION
    salary_balance = daily_salary * worked_days

    return salary_balance.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )