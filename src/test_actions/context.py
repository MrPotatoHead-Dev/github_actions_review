"""The GitHub Actions environment for one workflow run.

GitHub sets ``GITHUB_*`` variables before the first step. A workflow cannot
overwrite those names, so the manual workflow uses ``ACTIONS_EXAMPLE_*``
when it needs to preview a pull request or a push to main.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

LOCAL = "local"
PUSH = "push"
PULL_REQUEST = "pull_request"
SCHEDULE = "schedule"
WORKFLOW_DISPATCH = "workflow_dispatch"

MAIN_BRANCH = "main"


@dataclass(frozen=True)
class ActionContext:
    """Facts a job can see about the event that started the workflow."""

    event_name: str
    event_action: str = ""
    ref: str = ""
    ref_name: str = ""
    base_ref: str = ""
    head_ref: str = ""
    sha: str = ""
    head_sha: str = ""
    commit_message: str = ""
    actor: str = ""
    workflow: str = ""
    run_id: str = ""
    run_attempt: str = ""
    repository: str = ""
    server_url: str = "https://github.com"
    merged: bool | None = None

    @property
    def run_url(self) -> str:
        if self.repository and self.run_id:
            return f"{self.server_url}/{self.repository}/actions/runs/{self.run_id}"
        return ""

    @property
    def on_main(self) -> bool:
        return self.ref_name == MAIN_BRANCH or self.ref == f"refs/heads/{MAIN_BRANCH}"

    @property
    def pull_request_into_main(self) -> bool:
        return self.event_name == PULL_REQUEST and self.base_ref == MAIN_BRANCH


def _pick(env: Mapping[str, str], override: str, *fallbacks: str) -> str:
    value = env.get(override, "").strip()
    if value:
        return value
    for key in fallbacks:
        value = env.get(key, "").strip()
        if value:
            return value
    return ""


def _merged(value: str) -> bool | None:
    if value == "true":
        return True
    if value == "false":
        return False
    return None


def context_from_environ(env: Mapping[str, str] | None = None) -> ActionContext:
    """Build a context from the process environment."""

    source = os.environ if env is None else env
    event_name = _pick(source, "ACTIONS_EXAMPLE_EVENT", "GITHUB_EVENT_NAME") or LOCAL
    ref_name = _pick(source, "ACTIONS_EXAMPLE_REF_NAME", "GITHUB_REF_NAME")
    ref = _pick(source, "ACTIONS_EXAMPLE_REF", "GITHUB_REF")
    if not ref and ref_name:
        ref = f"refs/heads/{ref_name}"
    sha = _pick(source, "ACTIONS_EXAMPLE_SHA", "GITHUB_SHA")
    head_sha = _pick(source, "ACTIONS_EXAMPLE_HEAD_SHA") or sha
    return ActionContext(
        event_name=event_name,
        event_action=_pick(source, "ACTIONS_EXAMPLE_EVENT_ACTION"),
        ref=ref,
        ref_name=ref_name,
        base_ref=_pick(source, "ACTIONS_EXAMPLE_BASE_REF", "GITHUB_BASE_REF"),
        head_ref=_pick(source, "ACTIONS_EXAMPLE_HEAD_REF", "GITHUB_HEAD_REF"),
        sha=sha,
        head_sha=head_sha,
        commit_message=_pick(source, "ACTIONS_EXAMPLE_COMMIT_MESSAGE"),
        actor=_pick(source, "ACTIONS_EXAMPLE_ACTOR", "GITHUB_ACTOR"),
        workflow=_pick(source, "ACTIONS_EXAMPLE_WORKFLOW", "GITHUB_WORKFLOW"),
        run_id=_pick(source, "ACTIONS_EXAMPLE_RUN_ID", "GITHUB_RUN_ID"),
        run_attempt=_pick(source, "ACTIONS_EXAMPLE_RUN_ATTEMPT", "GITHUB_RUN_ATTEMPT"),
        repository=_pick(source, "ACTIONS_EXAMPLE_REPOSITORY", "GITHUB_REPOSITORY"),
        server_url=_pick(source, "ACTIONS_EXAMPLE_SERVER_URL", "GITHUB_SERVER_URL")
        or "https://github.com",
        merged=_merged(_pick(source, "ACTIONS_EXAMPLE_MERGED")),
    )
