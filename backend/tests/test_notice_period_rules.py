import pytest

from app.domain.notice_period_rules import validate_notice_period_type
from app.domain.notice_period_type import NoticePeriodType
from app.domain.termination_type import TerminationType


@pytest.mark.parametrize(
    ("termination_type", "notice_period_type"),
    [
        (
            TerminationType.DISMISSAL_WITHOUT_CAUSE,
            NoticePeriodType.WORKED,
        ),
        (
            TerminationType.DISMISSAL_WITHOUT_CAUSE,
            NoticePeriodType.INDEMNIFIED,
        ),
        (
            TerminationType.RESIGNATION,
            NoticePeriodType.WORKED,
        ),
        (
            TerminationType.RESIGNATION,
            NoticePeriodType.NOT_WORKED,
        ),
        (
            TerminationType.MUTUAL_AGREEMENT,
            NoticePeriodType.WORKED,
        ),
        (
            TerminationType.MUTUAL_AGREEMENT,
            NoticePeriodType.INDEMNIFIED,
        ),
    ],
)
def test_accepts_valid_notice_period_combinations(
    termination_type: TerminationType,
    notice_period_type: NoticePeriodType,
) -> None:
    validate_notice_period_type(
        termination_type=termination_type,
        notice_period_type=notice_period_type,
    )


@pytest.mark.parametrize(
    ("termination_type", "notice_period_type"),
    [
        (
            TerminationType.DISMISSAL_WITHOUT_CAUSE,
            NoticePeriodType.NOT_WORKED,
        ),
        (
            TerminationType.RESIGNATION,
            NoticePeriodType.INDEMNIFIED,
        ),
        (
            TerminationType.MUTUAL_AGREEMENT,
            NoticePeriodType.NOT_WORKED,
        ),
        (
            TerminationType.DISMISSAL_WITH_CAUSE,
            NoticePeriodType.WORKED,
        ),
        (
            TerminationType.DISMISSAL_WITH_CAUSE,
            NoticePeriodType.INDEMNIFIED,
        ),
        (
            TerminationType.DISMISSAL_WITH_CAUSE,
            NoticePeriodType.NOT_WORKED,
        ),
    ],
)
def test_rejects_invalid_notice_period_combinations(
    termination_type: TerminationType,
    notice_period_type: NoticePeriodType,
) -> None:
    with pytest.raises(ValueError):
        validate_notice_period_type(
            termination_type=termination_type,
            notice_period_type=notice_period_type,
        )


def test_accepts_missing_notice_period_type_for_backward_compatibility() -> None:
    validate_notice_period_type(
        termination_type=TerminationType.DISMISSAL_WITHOUT_CAUSE,
        notice_period_type=None,
    )