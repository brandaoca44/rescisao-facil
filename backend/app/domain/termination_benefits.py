from dataclasses import dataclass
from decimal import Decimal

from app.domain.termination_type import TerminationType


@dataclass(frozen=True)
class TerminationBenefits:
    """Informações por modalidade; não confirma disponibilidade ou concessão."""

    fgts_withdrawal_rate_under_saque_rescisao: Decimal
    unemployment_insurance_possible_by_termination_type: bool
    notes: tuple[str, ...]


def get_termination_benefits(
    termination_type: TerminationType,
) -> TerminationBenefits:
    """Aplica as regras gerais sem avaliar a situação individual do trabalhador."""
    # CLT, art. 484-A; regras de movimentação da CAIXA; Lei 7.998/1990.
    if termination_type == TerminationType.DISMISSAL_WITHOUT_CAUSE:
        rate, insurance = Decimal("1.00"), True
    elif termination_type == TerminationType.MUTUAL_AGREEMENT:
        rate, insurance = Decimal("0.80"), False
    elif termination_type in (
        TerminationType.RESIGNATION, TerminationType.DISMISSAL_WITH_CAUSE,
    ):
        rate, insurance = Decimal("0.00"), False
    else:
        raise NotImplementedError(
            f"Termination type '{termination_type}' is not supported."
        )

    if rate > 0:
        fgts_notes = (
            "O percentual de saque pressupõe a sistemática saque-rescisão "
            "e não confirma saldo disponível ou liberação imediata.",
            "Na sistemática saque-aniversário, a regra geral para este "
            "desligamento permite sacar a multa rescisória, sem liberar "
            "o restante do saldo por esse motivo. Regras extraordinárias "
            "e restrições da conta exigem verificação específica.",
        )
    else:
        fgts_notes = (
            "Esta modalidade não libera o saldo do FGTS por motivo de "
            "desligamento. Outras hipóteses legais de saque não são avaliadas.",
        )

    insurance_note = (
        "A concessão do seguro-desemprego depende dos demais requisitos "
        "legais, incluindo histórico salarial, solicitações anteriores, "
        "situação de desemprego, renda e benefícios recebidos."
        if insurance else
        "Esta modalidade de desligamento não permite o ingresso no "
        "seguro-desemprego por este vínculo."
    )
    return TerminationBenefits(rate, insurance, (*fgts_notes, insurance_note))
