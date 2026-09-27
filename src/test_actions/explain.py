"""Text for the job log and the GitHub job summary."""

from __future__ import annotations

from test_actions.context import LOCAL, PULL_REQUEST, PUSH, ActionContext
from test_actions.cron import WEEKDAY_AFTERNOON, describe_cron
from test_actions.rules import FAIL_MERGE_BRANCH, POST_MERGE_TOKEN, plans_for


def render(ctx: ActionContext) -> str:
    """Explain the current event in Markdown."""

    lines = [f"# {_title(ctx)}", "", _table(ctx), ""]
    lines.extend(_event_note(ctx))
    lines.extend(["## Workflows for this event", ""])
    plans = plans_for(ctx)
    if not plans:
        lines.append("No workflow in this repo listens for this event.")
        lines.append("")
        if ctx.event_name == LOCAL:
            lines.append(
                "Run `uv run python -m test_actions` after exporting "
                "`ACTIONS_EXAMPLE_EVENT` to preview one, or push the repository "
                "and open the Actions tab."
            )
            lines.append("")
    for plan in plans:
        lines.append(f"### {plan.name}")
        lines.append("")
        lines.append(f"File: `{plan.file}`")
        lines.append("")
        lines.append(plan.reason)
        lines.append("")
        if plan.suites:
            markers = ", ".join(f"`{suite}`" for suite in plan.suites)
            lines.append(f"Pytest markers: {markers}.")
        else:
            lines.append("Pytest markers: none. This run records the event and stops.")
        lines.append("")
    lines.extend(
        [
            "## Ways to turn a check red",
            "",
            f"- Name the pull request branch `{FAIL_MERGE_BRANCH}` and target main. "
            "Unit and integration stay green. The merge gate fails.",
            "- Put an uncommented line in `config/merge_blockers.txt`. "
            "The merge gate fails on the pull request.",
            f"- Put `{POST_MERGE_TOKEN}` in the tip commit message on main, "
            "or uncomment a line in `config/post_merge_failures.txt`. "
            "The pull request stays green. Merge to main fails after the push.",
            "- Open Actions, choose Manual, and set simulate failure. "
            "That run fails without a new commit.",
            "",
            "## Schedule",
            "",
            f"`{WEEKDAY_AFTERNOON}` — {describe_cron(WEEKDAY_AFTERNOON)}",
            "",
            "That is 10:15 in UTC−3. GitHub starts this only from the default branch, "
            "and the run can show up a few minutes late. The Run workflow button on "
            "Scheduled uses `workflow_dispatch`, so the cron-only test skips until "
            "the clock starts a run.",
            "",
        ]
    )
    return "\n".join(lines)


def _title(ctx: ActionContext) -> str:
    if ctx.event_name == PULL_REQUEST:
        action = ctx.event_action or "update"
        source = ctx.head_ref or "a branch"
        target = ctx.base_ref or "a base branch"
        return f"Pull request {action}: {source} → {target}"
    if ctx.event_name == PUSH and ctx.ref_name:
        return f"Push to {ctx.ref_name}"
    if ctx.event_name == PUSH:
        return "Push"
    if ctx.event_name == LOCAL:
        return "Local run"
    if ctx.workflow:
        return f"{ctx.event_name} ({ctx.workflow})"
    return ctx.event_name


def _table(ctx: ActionContext) -> str:
    message_label = "Pull request title" if ctx.event_name == PULL_REQUEST else "Commit message"
    merged = "—"
    if ctx.merged is True:
        merged = "true"
    elif ctx.merged is False:
        merged = "false"
    rows = [
        ("Event", ctx.event_name),
        ("Action", ctx.event_action),
        ("Workflow", ctx.workflow),
        ("Repository", ctx.repository),
        ("Actor", ctx.actor),
        ("Run", ctx.run_url or ctx.run_id),
        ("Attempt", ctx.run_attempt),
        ("Ref", ctx.ref),
        ("Ref name", ctx.ref_name),
        ("Head ref", ctx.head_ref),
        ("Base ref", ctx.base_ref),
        ("SHA", ctx.sha),
        ("Head SHA", ctx.head_sha),
        (message_label, _one_line(ctx.commit_message)),
        ("Merged", merged),
    ]
    lines = ["| Field | Value |", "| --- | --- |"]
    for label, value in rows:
        shown = value if value else "—"
        lines.append(f"| {label} | {shown.replace('|', '/')} |")
    return "\n".join(lines)


def _event_note(ctx: ActionContext) -> list[str]:
    if ctx.event_name == PULL_REQUEST:
        return [
            "On `pull_request`, `GITHUB_REF` is `refs/pull/<number>/merge` and "
            "`GITHUB_SHA` is a temporary merge of the head into the base. "
            "The branch you pushed is `GITHUB_HEAD_REF`. `GITHUB_REF_NAME` is "
            "`<number>/merge`.",
            "",
            "A new commit on an open pull request sends `synchronize`. "
            "That push also starts the Push workflow when the branch lives in this repository. "
            "You get two runs for one git push: one `push`, one `pull_request`.",
            "",
        ]
    if ctx.event_name == PUSH:
        return [
            "`GITHUB_SHA` on a push is the tip commit that was just pushed. "
            "`GITHUB_REF` is `refs/heads/<branch>`. Head ref and base ref stay empty "
            "because a push has no pull request attached.",
            "",
        ]
    return []


def _one_line(value: str) -> str:
    compact = " ".join(value.split())
    if len(compact) > 180:
        return compact[:177] + "..."
    return compact
