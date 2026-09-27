"""Which workflows and checks run for a GitHub event.

The YAML files decide what GitHub actually starts. These functions are the
same rules in Python so a test can state them, and so the explain command
can print them into the run log.
"""

from __future__ import annotations

from dataclasses import dataclass

from test_actions.context import MAIN_BRANCH, PULL_REQUEST, PUSH, SCHEDULE, WORKFLOW_DISPATCH, ActionContext

UNIT = "unit"
INTEGRATION = "integration"
MERGE_GATE = "merge_gate"
POST_MERGE = "post_merge"
SCHEDULED = "scheduled"

FAIL_MERGE_BRANCH = "demo/fail-merge"
POST_MERGE_TOKEN = "[fail-post-merge]"


@dataclass(frozen=True)
class WorkflowPlan:
    """One workflow file GitHub will start for this event."""

    name: str
    file: str
    suites: tuple[str, ...]
    reason: str


def is_fail_merge_branch(head_ref: str) -> bool:
    """True for ``demo/fail-merge`` and branches nested under that prefix."""

    return head_ref == FAIL_MERGE_BRANCH or head_ref.startswith(f"{FAIL_MERGE_BRANCH}/")


def plans_for(ctx: ActionContext) -> list[WorkflowPlan]:
    """Workflows in this repo that listen for ``ctx``."""

    if ctx.event_name == PUSH and ctx.ref_name == MAIN_BRANCH:
        return [
            WorkflowPlan(
                name="Push",
                file=".github/workflows/push.yml",
                suites=(UNIT, INTEGRATION),
                reason=(
                    "A merge lands on main as a push. This workflow runs the same "
                    "unit and integration tests it runs for every other branch."
                ),
            ),
            WorkflowPlan(
                name="Merge to main",
                file=".github/workflows/merge-main.yml",
                suites=(POST_MERGE,),
                reason=(
                    "This second workflow listens only to pushes of main. "
                    "A pull request can stay green while this check fails after the merge."
                ),
            ),
        ]
    if ctx.event_name == PUSH:
        branch = ctx.ref_name or ctx.ref or "this branch"
        return [
            WorkflowPlan(
                name="Push",
                file=".github/workflows/push.yml",
                suites=(UNIT, INTEGRATION),
                reason=(
                    f"A push updates {branch} immediately. "
                    "Pull request checks stay idle until a pull request exists for the branch."
                ),
            )
        ]
    if ctx.event_name == PULL_REQUEST and ctx.event_action == "closed":
        if ctx.merged is True:
            reason = (
                "This pull request was merged. GitHub also sends a push of the base "
                "branch. The Push and Merge to main runs for that commit hold the "
                "post-merge logs."
            )
        elif ctx.merged is False:
            reason = (
                "This pull request was closed and left the base branch unchanged. "
                "No push workflow runs for the close itself."
            )
        else:
            reason = (
                "Closing a pull request sends pull_request with action closed. "
                "Tests stay idle on that run. A merge also pushes the base branch."
            )
        return [
            WorkflowPlan(
                name="Pull request",
                file=".github/workflows/pull-request.yml",
                suites=(),
                reason=reason,
            )
        ]
    if ctx.event_name == PULL_REQUEST and ctx.base_ref == MAIN_BRANCH:
        return [
            WorkflowPlan(
                name="Pull request",
                file=".github/workflows/pull-request.yml",
                suites=(UNIT, INTEGRATION, MERGE_GATE),
                reason=(
                    "An open pull request into main runs the merge gate. "
                    "Branch protection can require that check before the merge button works."
                ),
            )
        ]
    if ctx.event_name == PULL_REQUEST:
        target = ctx.base_ref or "another branch"
        return [
            WorkflowPlan(
                name="Pull request",
                file=".github/workflows/pull-request.yml",
                suites=(UNIT, INTEGRATION),
                reason=(
                    f"This pull request targets {target}. "
                    "The merge gate job stays skipped until the base branch is main."
                ),
            )
        ]
    if ctx.event_name == SCHEDULE:
        return [
            WorkflowPlan(
                name="Scheduled",
                file=".github/workflows/scheduled.yml",
                suites=(UNIT, SCHEDULED),
                reason=(
                    "GitHub starts schedule events from the default branch. "
                    "The clock is UTC, and the run can begin a few minutes after the cron time."
                ),
            )
        ]
    if ctx.event_name == WORKFLOW_DISPATCH:
        return [
            WorkflowPlan(
                name="Manual",
                file=".github/workflows/manual.yml",
                suites=(UNIT, SCHEDULED),
                reason=(
                    "workflow_dispatch is the Run workflow button. "
                    "It records a run without waiting for a push or the cron clock."
                ),
            )
        ]
    return []


def merge_gate_blockers(ctx: ActionContext, file_blockers: list[str]) -> list[str]:
    """Reasons a pull request into main should fail the merge gate."""

    reasons = list(file_blockers)
    if is_fail_merge_branch(ctx.head_ref):
        reasons.append(
            f"{ctx.head_ref} is reserved so the merge gate fails while the other suites pass"
        )
    return reasons


def post_merge_failures(commit_message: str, file_failures: list[str]) -> list[str]:
    """Reasons a push to main should fail after a merge."""

    reasons = list(file_failures)
    if POST_MERGE_TOKEN in commit_message:
        reasons.append(f"the tip commit message contains {POST_MERGE_TOKEN}")
    return reasons


def gate_message(title: str, reasons: list[str], fix: str) -> str:
    """Pytest failure text that points at the switch you flipped."""

    bullets = "\n".join(f"- {reason}" for reason in reasons)
    return f"{title}\n{bullets}\n\n{fix}"
