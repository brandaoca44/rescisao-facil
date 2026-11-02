from app.domain.notice_period_type import NoticePeriodType


def test_notice_period_type_values() -> None:
    assert NoticePeriodType.WORKED.value == "worked"
    assert NoticePeriodType.INDEMNIFIED.value == "indemnified"
    assert NoticePeriodType.NOT_WORKED.value == "not_worked"