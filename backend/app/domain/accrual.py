from calendar import monthrange
from datetime import date, timedelta


MINIMUM_DAYS_FOR_ACCRUAL = 15
MONTHS_IN_VACATION_ACCRUAL_PERIOD = 12


def calculate_thirteenth_accrued_months(
    admission_date: date,
    termination_date: date,
) -> int:
    """Calcula os avos de 13º adquiridos no ano da rescisão."""

    if termination_date < admission_date:
        raise ValueError("Termination date cannot be before admission date.")

    termination_year = termination_date.year
    first_month = (
        admission_date.month
        if admission_date.year == termination_year
        else 1
    )

    accrued_months = 0

    for month in range(first_month, termination_date.month + 1):
        first_worked_day = (
            admission_date.day
            if (
                admission_date.year == termination_year
                and month == admission_date.month
            )
            else 1
        )

        last_worked_day = (
            termination_date.day
            if month == termination_date.month
            else monthrange(termination_year, month)[1]
        )

        worked_days = last_worked_day - first_worked_day + 1

        if worked_days >= MINIMUM_DAYS_FOR_ACCRUAL:
            accrued_months += 1

    return accrued_months


def _add_months(value: date, months: int) -> date:
    """Adiciona meses preservando o dia quando possível."""

    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1

    last_day = monthrange(year, month)[1]
    day = min(value.day, last_day)

    return date(year, month, day)


def calculate_current_vacation_period_start(
    admission_date: date,
    reference_date: date,
) -> date:
    """Retorna o início do período aquisitivo vigente na data de referência."""

    if reference_date < admission_date:
        raise ValueError("Reference date cannot be before admission date.")

    completed_periods = calculate_completed_vacation_periods(
        admission_date, reference_date,
    )
    return _vacation_anniversary(admission_date, completed_periods)


def _vacation_anniversary(admission_date: date, years: int) -> date:
    year = admission_date.year + years
    last_day = monthrange(year, admission_date.month)[1]
    if admission_date.day > last_day:
        # Dia inexistente: primeiro dia subsequente (Lei 810/1949, art. 3º).
        return date(year, admission_date.month, last_day) + timedelta(days=1)
    return admission_date.replace(year=year)


def calculate_completed_vacation_periods(
    admission_date: date, reference_date: date,
) -> int:
    """Conta períodos de 12 meses com o último dia do vínculo incluído."""
    if reference_date < admission_date:
        raise ValueError("Reference date cannot be before admission date.")
    next_day = reference_date + timedelta(days=1)
    years = next_day.year - admission_date.year
    if next_day < _vacation_anniversary(admission_date, years):
        years -= 1
    return max(years, 0)


def calculate_vacation_accrued_months(
    admission_date: date,
    termination_date: date,
) -> int:
    """Calcula os avos de férias do período aquisitivo incompleto."""

    if termination_date < admission_date:
        raise ValueError("Termination date cannot be before admission date.")

    period_start = calculate_current_vacation_period_start(
        admission_date=admission_date,
        reference_date=termination_date,
    )

    accrued_months = 0
    current_month_start = period_start

    while accrued_months < MONTHS_IN_VACATION_ACCRUAL_PERIOD:
        next_month_start = _add_months(current_month_start, 1)

        if termination_date >= next_month_start:
            accrued_months += 1
            current_month_start = next_month_start
            continue

        partial_days = (termination_date - current_month_start).days + 1

        if partial_days >= MINIMUM_DAYS_FOR_ACCRUAL:
            accrued_months += 1

        break

    return accrued_months