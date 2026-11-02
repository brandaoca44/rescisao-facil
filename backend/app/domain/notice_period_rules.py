from app.domain.notice_period_type import NoticePeriodType
from app.domain.termination_type import TerminationType


ALLOWED_NOTICE_PERIOD_TYPES = {
    TerminationType.DISMISSAL_WITHOUT_CAUSE: {
        NoticePeriodType.WORKED,
        NoticePeriodType.INDEMNIFIED,
    },
    TerminationType.RESIGNATION: {
        NoticePeriodType.WORKED,
        NoticePeriodType.NOT_WORKED,
    },
    TerminationType.MUTUAL_AGREEMENT: {
        NoticePeriodType.WORKED,
        NoticePeriodType.INDEMNIFIED,
    },
    TerminationType.DISMISSAL_WITH_CAUSE: set(),
}


def validate_notice_period_type(
    termination_type: TerminationType,
    notice_period_type: NoticePeriodType | None,
) -> None:
    """
    Valida se a situação do aviso prévio é compatível
    com a modalidade de desligamento.
    """

    # Mantém compatibilidade com chamadas antigas enquanto
    # o novo fluxo de aviso ainda está sendo integrado.
    if notice_period_type is None:
        return

    allowed_types = ALLOWED_NOTICE_PERIOD_TYPES[termination_type]

    if notice_period_type not in allowed_types:
        raise ValueError(
            "Notice period type is not allowed for this termination type."
        )