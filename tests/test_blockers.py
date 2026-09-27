import pytest

from test_actions.blockers import active_lines


@pytest.mark.unit
def test_comments_and_blank_lines_are_ignored(tmp_path):
    path = tmp_path / "blockers.txt"
    path.write_text("# note\n\n  \nreal blocker\n\t# indented comment\n", encoding="utf-8")
    assert active_lines(path) == ["real blocker"]


@pytest.mark.unit
def test_a_missing_file_is_reported(tmp_path):
    missing = tmp_path / "nope.txt"
    assert active_lines(missing) == ["missing nope.txt"]
