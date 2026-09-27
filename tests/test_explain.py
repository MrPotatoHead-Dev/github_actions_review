import pytest

from test_actions.context import ActionContext
from test_actions.explain import render


@pytest.mark.unit
def test_pull_request_log_names_both_refs_and_the_merge_gate():
    text = render(
        ActionContext(
            event_name="pull_request",
            event_action="opened",
            ref="refs/pull/7/merge",
            ref_name="7/merge",
            base_ref="main",
            head_ref="feature/logs",
            sha="merge-sha",
            head_sha="head-sha",
            repository="MrPotatoHead-Dev/test-actions",
            run_id="7",
        )
    )
    assert "feature/logs → main" in text
    assert "refs/pull/7/merge" in text
    assert "GITHUB_HEAD_REF" in text
    assert "Merge gate" in text or "merge gate" in text
    assert "`merge_gate`" in text
    assert "actions/runs/7" in text


@pytest.mark.unit
def test_push_to_main_log_lists_both_workflows():
    text = render(ActionContext(event_name="push", ref_name="main", sha="abc", commit_message="ship it"))
    assert "Push to main" in text
    assert ".github/workflows/push.yml" in text
    assert ".github/workflows/merge-main.yml" in text
    assert "`post_merge`" in text


@pytest.mark.unit
def test_feature_push_log_stays_on_the_push_workflow():
    text = render(ActionContext(event_name="push", ref_name="feature/logs"))
    assert ".github/workflows/merge-main.yml" not in text
    assert ".github/workflows/push.yml" in text
    assert "feature/logs" in text


@pytest.mark.unit
def test_local_log_explains_how_to_preview_an_event():
    text = render(ActionContext(event_name="local"))
    assert "ACTIONS_EXAMPLE_EVENT" in text
    assert "15 13 * * 1-5" in text
