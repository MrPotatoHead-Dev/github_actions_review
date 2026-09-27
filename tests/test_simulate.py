import os

import pytest


@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.merge_gate
@pytest.mark.post_merge
@pytest.mark.scheduled
def test_simulated_failure_switch():
    """The Manual workflow sets SIMULATE_FAILURE=1 to produce a red log."""

    if os.environ.get("SIMULATE_FAILURE") == "1":
        pytest.fail(
            "Simulated failure from the Manual workflow. "
            "The traceback above the summary is the log to review. "
            "Run the workflow again with simulate failure turned off for a green result."
        )
