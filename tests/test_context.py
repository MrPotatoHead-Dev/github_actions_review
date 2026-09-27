import pytest

from test_actions.context import LOCAL, context_from_environ


@pytest.mark.unit
def test_missing_github_env_is_a_local_run():
    ctx = context_from_environ({})
    assert ctx.event_name == LOCAL
    assert ctx.run_url == ""


@pytest.mark.unit
def test_github_names_fill_the_context():
    ctx = context_from_environ(
        {
            "GITHUB_EVENT_NAME": "push",
            "GITHUB_REF": "refs/heads/feature/logs",
            "GITHUB_REF_NAME": "feature/logs",
            "GITHUB_SHA": "abc123",
            "GITHUB_ACTOR": "jaden",
            "GITHUB_WORKFLOW": "Push",
            "GITHUB_RUN_ID": "99",
            "GITHUB_RUN_ATTEMPT": "2",
            "GITHUB_REPOSITORY": "MrPotatoHead-Dev/test-actions",
            "GITHUB_SERVER_URL": "https://github.com",
        }
    )
    assert ctx.event_name == "push"
    assert ctx.ref_name == "feature/logs"
    assert ctx.on_main is False
    assert ctx.head_sha == "abc123"
    assert ctx.run_url == "https://github.com/MrPotatoHead-Dev/test-actions/actions/runs/99"
    assert ctx.run_attempt == "2"


@pytest.mark.unit
def test_example_overrides_win_over_github_names():
    ctx = context_from_environ(
        {
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REF_NAME": "main",
            "ACTIONS_EXAMPLE_EVENT": "pull_request",
            "ACTIONS_EXAMPLE_BASE_REF": "main",
            "ACTIONS_EXAMPLE_HEAD_REF": "demo/fail-merge",
            "ACTIONS_EXAMPLE_MERGED": "true",
        }
    )
    assert ctx.event_name == "pull_request"
    assert ctx.pull_request_into_main is True
    assert ctx.head_ref == "demo/fail-merge"
    assert ctx.merged is True
    assert ctx.ref == "refs/heads/main"


@pytest.mark.unit
def test_blank_override_falls_through():
    ctx = context_from_environ(
        {
            "ACTIONS_EXAMPLE_EVENT": "  ",
            "GITHUB_EVENT_NAME": "schedule",
            "GITHUB_REF_NAME": "main",
        }
    )
    assert ctx.event_name == "schedule"
    assert ctx.on_main is True
