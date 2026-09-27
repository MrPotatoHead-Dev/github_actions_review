import pytest

from test_actions.blockers import active_lines
from test_actions.context import MAIN_BRANCH, PULL_REQUEST, context_from_environ
from test_actions.paths import MERGE_BLOCKERS_PATH
from test_actions.rules import gate_message, merge_gate_blockers

FILE_FIX = (
    "Delete the active lines in config/merge_blockers.txt or comment them out, "
    "then push the pull request branch again."
)
BRANCH_FIX = (
    "Use a branch name other than demo/fail-merge when you want this pull request "
    "to pass. Keep that name when you want to study a red merge gate."
)


@pytest.mark.merge_gate
def test_merge_blocker_file_is_clear():
    reasons = active_lines(MERGE_BLOCKERS_PATH)
    if reasons:
        pytest.fail(
            gate_message(
                "Merge gate failed because config/merge_blockers.txt has active lines.",
                reasons,
                FILE_FIX,
            )
        )


@pytest.mark.merge_gate
def test_branch_is_allowed_into_main():
    ctx = context_from_environ()
    if ctx.event_name != PULL_REQUEST:
        pytest.skip("the reserved branch name is checked on pull_request events")
    if ctx.base_ref != MAIN_BRANCH:
        pytest.skip(f"the merge gate runs for base main; this base is {ctx.base_ref or 'unset'}")
    reasons = merge_gate_blockers(ctx, [])
    if reasons:
        pytest.fail(
            gate_message(
                "Merge gate failed because of the pull request branch.",
                reasons,
                BRANCH_FIX,
            )
        )
