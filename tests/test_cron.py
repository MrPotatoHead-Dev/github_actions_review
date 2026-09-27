import pytest

from test_actions.cron import WEEKDAY_AFTERNOON, describe_cron


@pytest.mark.unit
def test_weekday_afternoon_is_1315_utc_monday_through_friday():
    assert WEEKDAY_AFTERNOON == "15 13 * * 1-5"
    assert describe_cron(WEEKDAY_AFTERNOON) == "At 13:15, Monday through Friday, UTC."


@pytest.mark.unit
@pytest.mark.parametrize(
    ("expression", "sentence"),
    [
        ("0 0 * * *", "At 00:00, every day, UTC."),
        ("*/10 * * * *", "Every 10 minutes, every day, UTC."),
        ("0 * * * 1,3,5", "At minute 0 past every hour, on Monday, Wednesday, and Friday, UTC."),
        ("30 4 * * 0", "At 04:30, on Sunday, UTC."),
        ("30 4 * * 7", "At 04:30, on Sunday, UTC."),
    ],
)
def test_other_cron_shapes(expression, sentence):
    assert describe_cron(expression) == sentence


@pytest.mark.unit
def test_restricted_day_and_weekday_together_are_rejected():
    with pytest.raises(ValueError, match="OR"):
        describe_cron("0 0 1 * 1")
