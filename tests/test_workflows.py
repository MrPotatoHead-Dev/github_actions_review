import pytest

from test_actions.cron import WEEKDAY_AFTERNOON
from test_actions.paths import WORKFLOWS_DIR
from test_actions.rules import FAIL_MERGE_BRANCH, POST_MERGE_TOKEN


def _text(name: str) -> str:
    return (WORKFLOWS_DIR / name).read_text(encoding="utf-8")


@pytest.mark.integration
def test_push_workflow_listens_to_every_branch():
    text = _text("push.yml")
    assert "push:" in text
    assert '"**"' in text or "'**'" in text
    assert "marker: unit" in text
    assert "marker: integration" in text
    assert "merge_gate" not in text
    assert "post_merge" not in text


@pytest.mark.integration
def test_pull_request_workflow_gates_merges_into_main():
    text = _text("pull-request.yml")
    for action in ("opened", "synchronize", "reopened", "closed"):
        assert action in text
    assert "marker: merge_gate" in text
    assert "github.base_ref == 'main'" in text
    assert "github.event.action != 'closed'" in text
    assert FAIL_MERGE_BRANCH not in text


@pytest.mark.integration
def test_merge_main_workflow_is_the_post_merge_check():
    text = _text("merge-main.yml")
    assert "branches:" in text
    assert "- main" in text
    assert "marker: post_merge" in text
    assert "github.event.head_commit.message" in text
    assert "pull_request:" not in text


@pytest.mark.integration
def test_scheduled_workflow_uses_the_documented_cron():
    text = _text("scheduled.yml")
    assert f"cron: '{WEEKDAY_AFTERNOON}'" in text
    assert "workflow_dispatch:" in text
    assert "marker: scheduled" in text


@pytest.mark.integration
def test_manual_workflow_can_preview_a_failure():
    text = _text("manual.yml")
    assert "workflow_dispatch:" in text
    assert "simulate_failure" in text
    assert "pretend_branch" in text
    assert POST_MERGE_TOKEN in text
    assert "marker: ${{ inputs.suite }}" in text


@pytest.mark.integration
def test_shared_workflows_and_setup_exist():
    assert "workflow_call:" in _text("pytest.yml")
    assert "upload-artifact" in _text("pytest.yml")
    assert "workflow_call:" in _text("explain.yml")
    setup = WORKFLOWS_DIR.parent / "actions" / "setup" / "action.yml"
    assert setup.is_file()
    assert "composite" in setup.read_text(encoding="utf-8")
