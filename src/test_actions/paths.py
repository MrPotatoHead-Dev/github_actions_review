"""Locations the tests and the explain command share with the workflows."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MERGE_BLOCKERS_PATH = REPO_ROOT / "config" / "merge_blockers.txt"
POST_MERGE_FAILURES_PATH = REPO_ROOT / "config" / "post_merge_failures.txt"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
