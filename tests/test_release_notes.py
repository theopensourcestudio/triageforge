import subprocess
from pathlib import Path

from triageforge.release_notes import generate_release_notes


def _git(path: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)


def test_release_notes_group_conventional_commits(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "a.txt").write_text("a")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "feat: add useful thing")
    notes = generate_release_notes(tmp_path)
    assert "## Features" in notes
    assert "add useful thing" in notes
