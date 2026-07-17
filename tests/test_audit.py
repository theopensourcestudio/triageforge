from pathlib import Path

from triageforge.audit import audit_repository


def test_empty_repository_scores_zero(tmp_path: Path) -> None:
    report = audit_repository(tmp_path)
    assert report.percentage == 0
    assert all(item.status == "missing" for item in report.findings)


def test_readme_and_license_add_points(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("hello")
    (tmp_path / "LICENSE").write_text("MIT")
    report = audit_repository(tmp_path)
    assert report.score >= 20
