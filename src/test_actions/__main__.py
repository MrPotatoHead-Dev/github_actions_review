"""Print the run explanation. Workflows invoke this as ``python -m test_actions``."""

from __future__ import annotations

import os

from test_actions.context import context_from_environ
from test_actions.explain import render


def main() -> None:
    text = render(context_from_environ())
    print(text, end="" if text.endswith("\n") else "\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as handle:
            handle.write(text)
            if not text.endswith("\n"):
                handle.write("\n")


if __name__ == "__main__":
    main()
