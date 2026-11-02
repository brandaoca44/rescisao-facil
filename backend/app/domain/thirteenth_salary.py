from dataclasses import dataclass
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

@dataclass(frozen=True)
class ThirteenthPreviousPayment:
    gross_amount: Decimal = Decimal("0.00")
    inss_withheld: Decimal = Decimal("0.00")
    irrf_withheld: Decimal = Decimal("0.00")
    fgts_deposited: Decimal = Decimal("0.00")


@dataclass(frozen=True)
class ThirteenthSettlement:
    gross_balance: Decimal
    inss_remaining: Decimal
    irrf_remaining: Decimal


def settle_thirteenth_salary(
    gross_amount: Decimal,
    current_year_amount: Decimal,
    inss_assessed: Decimal,
    irrf_assessed: Decimal,
    current_year_fgts: Decimal,
    previous: ThirteenthPreviousPayment,
) -> ThirteenthSettlement:
    """Compensa histórico do ano do desligamento, sem simular restituições."""
    values = (
        gross_amount, current_year_amount, inss_assessed, irrf_assessed,
        current_year_fgts, previous.gross_amount, previous.inss_withheld,
        previous.irrf_withheld, previous.fgts_deposited,
    )
    if any(not value.is_finite() or value < 0 for value in values):
        raise ValueError("Thirteenth settlement values must be finite and non-negative.")
    if previous.inss_withheld + previous.irrf_withheld > previous.gross_amount:
        raise ValueError("Previous thirteenth withholdings exceed the previous gross payment.")
    if previous.gross_amount > current_year_amount:
        raise ValueError(
            "Previous thirteenth gross payment exceeds the current-year entitlement; "
            "recovery of excess advances is not supported."
        )
    if previous.inss_withheld > inss_assessed or previous.irrf_withheld > irrf_assessed:
        raise ValueError(
            "Previous thirteenth withholdings exceed the reassessed tax; "
            "tax refunds require a separate review."
        )
    if previous.fgts_deposited > current_year_fgts:
        raise ValueError(
            "Previous thirteenth FGTS exceeds the current-year deposit; "
            "FGTS refunds require a separate review."
        )
    if previous.gross_amount == 0 and previous.fgts_deposited > 0:
        raise ValueError("Previous thirteenth FGTS requires a previous gross payment.")
    return ThirteenthSettlement(
        gross_balance=gross_amount - previous.gross_amount,
        inss_remaining=inss_assessed - previous.inss_withheld,
        irrf_remaining=irrf_assessed - previous.irrf_withheld,
    )
