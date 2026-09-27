"""Read the on/off switches stored as comment files."""

from pathlib import Path


def active_lines(path: Path) -> list[str]:
    """Return non-comment lines. A missing file is itself a failure reason."""

    if not path.is_file():
        return [f"missing {path.name}"]
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines
