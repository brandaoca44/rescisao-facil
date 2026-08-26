from datetime import date, timedelta

from decimal import Decimal, ROUND_HALF_UP

BASE_NOTICE_DAYS = 30
ADDITIONAL_DAYS_PER_YEAR = 3
MAX_ADDITIONAL_DAYS = 60
MAX_NOTICE_DAYS = 90
DAYS_IN_MONTH_FOR_NOTICE_CALCULATION = Decimal("30")
MONEY_QUANTIZER = Decimal("0.01")

def calculate_projected_termination_date(
    termination_date: date,
    notice_period_days: int,
) -> date:
    """Calcula a data projetada pelo aviso prévio indenizado."""

    if notice_period_days < 0:
        raise ValueError("Notice period days cannot be negative.")

    return termination_date + timedelta(days=notice_period_days)

def calculate_notice_period_days(
    admission_date: date,
    termination_date: date,
) -> int:
    """Calcula os dias de aviso prévio proporcional ao tempo de serviço."""

    if termination_date < admission_date:
        raise ValueError("Termination date cannot be before admission date.")

    completed_years = termination_date.year - admission_date.year

    anniversary = admission_date.replace(year=termination_date.year)

    if termination_date < anniversary:
        completed_years -= 1

    additional_days = min(
        completed_years * ADDITIONAL_DAYS_PER_YEAR,
        MAX_ADDITIONAL_DAYS,
    )

    return min(
        BASE_NOTICE_DAYS + additional_days,
        MAX_NOTICE_DAYS,
    )

def calculate_notice_period_value(
    monthly_salary: Decimal,
    notice_period_days: int,
) -> Decimal:
    """Calcula o valor do aviso prévio indenizado."""

    if monthly_salary < 0:
        raise ValueError("Monthly salary cannot be negative.")

    if notice_period_days < 0:
        raise ValueError("Notice period days cannot be negative.")

    notice_value = (
        monthly_salary
        / DAYS_IN_MONTH_FOR_NOTICE_CALCULATION
        * notice_period_days
    )

    return notice_value.quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )