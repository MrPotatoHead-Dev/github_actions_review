import pytest

from test_actions.context import ActionContext
from test_actions.rules import (
    FAIL_MERGE_BRANCH,
    INTEGRATION,
    MERGE_GATE,
    POST_MERGE,
    POST_MERGE_TOKEN,
    SCHEDULED,
    UNIT,
    gate_message,
    is_fail_merge_branch,
    merge_gate_blockers,
    plans_for,
    post_merge_failures,
)


def _ctx(**kwargs) -> ActionContext:
    return ActionContext(**kwargs)


@pytest.mark.unit
def test_push_to_a_feature_branch_runs_push_only():
    plans = plans_for(_ctx(event_name="push", ref_name="feature/logs"))
    assert [plan.name for plan in plans] == ["Push"]
    assert plans[0].suites == (UNIT, INTEGRATION)


@pytest.mark.unit
def test_push_to_main_also_runs_the_post_merge_workflow():
    plans = plans_for(_ctx(event_name="push", ref_name="main"))
    assert [plan.name for plan in plans] == ["Push", "Merge to main"]
    assert plans[1].suites == (POST_MERGE,)


@pytest.mark.unit
def test_pull_request_into_main_includes_the_merge_gate():
    plans = plans_for(
        _ctx(
            event_name="pull_request",
            event_action="synchronize",
            base_ref="main",
            head_ref="feature/logs",
        )
    )
    assert plans[0].suites == (UNIT, INTEGRATION, MERGE_GATE)


@pytest.mark.unit
def test_pull_request_into_another_branch_skips_the_merge_gate():
    plans = plans_for(
        _ctx(
            event_name="pull_request",
            event_action="opened",
            base_ref="release/1",
            head_ref="feature/logs",
        )
    )
    assert plans[0].suites == (UNIT, INTEGRATION)
    assert "release/1" in plans[0].reason


@pytest.mark.unit
def test_closed_pull_request_records_the_event_without_tests():
    merged = plans_for(
        _ctx(event_name="pull_request", event_action="closed", base_ref="main", merged=True)
    )
    abandoned = plans_for(
        _ctx(event_name="pull_request", event_action="closed", base_ref="main", merged=False)
    )
    assert merged[0].suites == ()
    assert "merged" in merged[0].reason
    assert abandoned[0].suites == ()
    assert "unchanged" in abandoned[0].reason


@pytest.mark.unit
def test_schedule_and_manual_runs_use_their_own_workflows():
    cron = plans_for(_ctx(event_name="schedule", ref_name="main"))
    manual = plans_for(_ctx(event_name="workflow_dispatch", ref_name="main"))
    assert cron[0].file.endswith("scheduled.yml")
    assert cron[0].suites == (UNIT, SCHEDULED)
    assert manual[0].file.endswith("manual.yml")


@pytest.mark.unit
def test_local_event_starts_nothing():
    assert plans_for(_ctx(event_name="local")) == []


@pytest.mark.unit
def test_fail_merge_branch_prefix():
    assert is_fail_merge_branch(FAIL_MERGE_BRANCH)
    assert is_fail_merge_branch(f"{FAIL_MERGE_BRANCH}/deeper")
    assert is_fail_merge_branch("demo/fail-merge-extra") is False
    assert is_fail_merge_branch("feature/ok") is False


@pytest.mark.unit
def test_merge_gate_collects_file_lines_and_the_reserved_branch():
    ctx = _ctx(event_name="pull_request", base_ref="main", head_ref=FAIL_MERGE_BRANCH)
    reasons = merge_gate_blockers(ctx, ["changelog"])
    assert reasons == [
        "changelog",
        f"{FAIL_MERGE_BRANCH} is reserved so the merge gate fails while the other suites pass",
    ]


@pytest.mark.unit
def test_post_merge_token_is_independent_of_the_branch_name():
    reasons = post_merge_failures(f"land on main {POST_MERGE_TOKEN}", ["stale fixture"])
    assert "stale fixture" in reasons[0]
    assert POST_MERGE_TOKEN in reasons[1]
    assert post_merge_failures("Merge pull request #4", []) == []


@pytest.mark.unit
def test_gate_message_lists_each_reason_and_the_fix():
    text = gate_message("Merge gate failed.", ["one", "two"], "Push a fix.")
    assert "one" in text
    assert "two" in text
    assert text.endswith("Push a fix.")
