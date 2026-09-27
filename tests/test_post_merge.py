import pytest

from test_actions.blockers import active_lines
from test_actions.context import MAIN_BRANCH, PUSH, context_from_environ
from test_actions.paths import POST_MERGE_FAILURES_PATH
from test_actions.rules import POST_MERGE_TOKEN, gate_message, post_merge_failures

FILE_FIX = (
    "Remove the active lines from config/post_merge_failures.txt on main. "
    "The pull request workflow ignores this file, so main stays red until a "
    "later push deletes those lines."
)
MESSAGE_FIX = (
    f"Push another commit to main whose message does not contain {POST_MERGE_TOKEN}. "
    "The failing run stays in the Actions history."
)


@pytest.mark.post_merge
def test_post_merge_failure_file_is_clear():
    reasons = active_lines(POST_MERGE_FAILURES_PATH)
    if reasons:
        pytest.fail(
            gate_message(
                "Post-merge check failed because config/post_merge_failures.txt has active lines.",
                reasons,
                FILE_FIX,
            )
        )


@pytest.mark.post_merge
def test_tip_commit_on_main_is_allowed():
    ctx = context_from_environ()
    if ctx.event_name != PUSH:
        pytest.skip("the commit message is checked on push events")
    if ctx.ref_name != MAIN_BRANCH:
        pytest.skip(f"post-merge checks run on main; this ref is {ctx.ref_name or 'unset'}")
    reasons = post_merge_failures(ctx.commit_message, [])
    if reasons:
        pytest.fail(
            gate_message(
                "Post-merge check failed because of the tip commit on main.",
                reasons,
                MESSAGE_FIX,
            )
        )
