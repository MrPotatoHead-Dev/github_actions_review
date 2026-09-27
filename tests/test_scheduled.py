import pytest

from test_actions.context import SCHEDULE, context_from_environ
from test_actions.cron import WEEKDAY_AFTERNOON, describe_cron
from test_actions.paths import WORKFLOWS_DIR


@pytest.mark.scheduled
def test_schedule_matches_the_workflow_file():
    text = (WORKFLOWS_DIR / "scheduled.yml").read_text(encoding="utf-8")
    assert f"cron: '{WEEKDAY_AFTERNOON}'" in text
    assert "Monday through Friday" in describe_cron(WEEKDAY_AFTERNOON)


@pytest.mark.scheduled
def test_this_run_was_started_by_cron():
    ctx = context_from_environ()
    if ctx.event_name == "workflow_dispatch":
        pytest.skip(
            "Run workflow records workflow_dispatch. "
            "The weekday cron records event schedule, and that run is the one that passes here."
        )
    if ctx.event_name != SCHEDULE:
        pytest.skip("this assertion runs when GitHub starts the workflow from cron")
    assert ctx.ref_name == "main"
