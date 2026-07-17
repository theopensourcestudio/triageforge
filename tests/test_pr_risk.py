import subprocess
from pathlib import Path

from triageforge.pr_risk import analyze_diff


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args], check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def test_auth_change_increases_risk(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "app.py").write_text("print('a')\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "initial")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "auth.py").write_text("def login():\n    return True\n")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "feat: authentication")
    result = analyze_diff(tmp_path, base, "HEAD")
    assert result.score >= 20
    assert any("authentication" in reason for reason in result.reasons)
