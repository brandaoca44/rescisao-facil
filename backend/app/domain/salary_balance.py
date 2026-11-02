from calendar import monthrange
from datetime import date
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

def calculate_salary_balance_for_dates(
    monthly_salary: Decimal,
    admission_date: date,
    termination_date: date,
) -> Decimal:
    """Aplica a convenção de 30 dias da V1 ao intervalo efetivamente trabalhado."""
    if termination_date < admission_date:
        raise ValueError("Termination date cannot be before admission date.")

    month_start = termination_date.replace(day=1)
    first_worked_day = max(admission_date, month_start)
    worked_days = (termination_date - first_worked_day).days + 1
    last_day = monthrange(termination_date.year, termination_date.month)[1]
    if first_worked_day == month_start and termination_date.day == last_day:
        worked_days = 30

    return calculate_salary_balance(monthly_salary, min(worked_days, 30))
