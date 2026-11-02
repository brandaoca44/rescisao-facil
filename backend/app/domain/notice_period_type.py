from enum import Enum


class NoticePeriodType(str, Enum):
    """Situação do aviso prévio na rescisão."""

    WORKED = "worked"
    INDEMNIFIED = "indemnified"
    NOT_WORKED = "not_worked"