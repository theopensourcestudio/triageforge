from triageforge.triage import triage_issue


def test_bug_triage_requests_reproduction() -> None:
    result = triage_issue(
        "Application crashes", "The application crashes immediately after launch."
    )
    assert "bug" in result.labels
    assert any("reproduction" in item.lower() for item in result.needs_information)


def test_security_is_urgent() -> None:
    result = triage_issue("Security vulnerability", "A secret token is exposed in logs.")
    assert result.priority == "urgent"
    assert "security" in result.labels
