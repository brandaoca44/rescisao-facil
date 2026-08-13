from enum import StrEnum


class TerminationType(StrEnum):
    """Modalidades de rescisão suportadas pela primeira versão."""

    DISMISSAL_WITHOUT_CAUSE = "dismissal_without_cause"
    RESIGNATION = "resignation"
    MUTUAL_AGREEMENT = "mutual_agreement"
    DISMISSAL_WITH_CAUSE = "dismissal_with_cause"