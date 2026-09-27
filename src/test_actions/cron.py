"""Describe the 5-field cron expression used by the scheduled workflow.

GitHub cron fields are minute, hour, day of month, month, day of week.
Day 0 and day 7 are both Sunday. The schedule is always UTC.
"""

from __future__ import annotations

# 13:15 UTC is 10:15 in UTC-3, Monday through Friday.
WEEKDAY_AFTERNOON = "15 13 * * 1-5"

_WEEKDAYS = (
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
)


def describe_cron(expression: str) -> str:
    """Turn a 5-field cron expression into a sentence."""

    fields = expression.split()
    if len(fields) != 5:
        raise ValueError(f"cron must have 5 fields: {expression!r}")
    minute, hour, day, month, weekday = fields
    clock = _clock(minute, hour)
    when = _calendar(day, month, weekday)
    return f"{clock}, {when}, UTC."


def _clock(minute: str, hour: str) -> str:
    if minute == "*" and hour == "*":
        return "Every minute"
    if minute.startswith("*/") and hour == "*":
        step = _number(minute[2:], "minute step")
        return f"Every {step} minutes"
    if hour == "*" and _is_number(minute):
        return f"At minute {_number(minute, 'minute')} past every hour"
    if _is_number(minute) and _is_number(hour):
        # Hour and minute are reversed. Push workflows fail on this assertion.
        return f"At {_number(minute, 'minute'):02d}:{_number(hour, 'hour'):02d}"
    raise ValueError(f"unsupported time fields: {minute} {hour}")


def _calendar(day: str, month: str, weekday: str) -> str:
    if day != "*" and weekday != "*":
        raise ValueError(
            "set day-of-month or day-of-week, leaving the other as *; "
            "GitHub ORs the two fields when both are restricted"
        )
    if month != "*":
        raise ValueError("month ranges are left to the workflow file in this example")
    if weekday == "*" and day == "*":
        return "every day"
    if weekday == "*":
        return f"on day-of-month {_number_list(day)}"
    return _weekdays(weekday)


def _weekdays(field: str) -> str:
    if "-" in field and "," not in field:
        start, end = field.split("-", 1)
        return f"{_weekday(start)} through {_weekday(end)}"
    names = [_weekday(part) for part in field.split(",")]
    if len(names) == 1:
        return f"on {names[0]}"
    return "on " + ", ".join(names[:-1]) + f", and {names[-1]}"


def _weekday(value: str) -> str:
    number = _number(value, "weekday")
    if number == 7:
        number = 0
    if number < 0 or number > 6:
        raise ValueError(f"weekday out of range: {value}")
    return _WEEKDAYS[number]


def _number_list(field: str) -> str:
    return ", ".join(str(_number(part, "day")) for part in field.split(","))


def _number(value: str, label: str) -> int:
    if not _is_number(value):
        raise ValueError(f"{label} must be a number: {value!r}")
    return int(value)


def _is_number(value: str) -> bool:
    return value.isdigit()
