from pathlib import Path

from oss_maintainer_audit.audit import audit_repository


def test_audit_scores_expected_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")

    result = audit_repository(tmp_path)

    assert result.total == 10
    assert result.passed == 3
    assert result.score_percent == 30


def test_audit_accepts_github_issue_template_directory(tmp_path: Path) -> None:
    issue_template_dir = tmp_path / ".github" / "ISSUE_TEMPLATE"
    issue_template_dir.mkdir(parents=True)

    result = audit_repository(tmp_path)
    issue_template = next(check for check in result.checks if check.name == "Issue templates")

    assert issue_template.passed is True


def test_audit_can_disable_checks(tmp_path: Path) -> None:
    result = audit_repository(tmp_path, disabled_checks=("License", "Security policy"))
    names = {check.name for check in result.checks}

    assert "License" not in names
    assert "Security policy" not in names


def test_audit_can_override_required_files(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "overview.md").write_text("# Overview\n", encoding="utf-8")

    result = audit_repository(tmp_path, required_files={"README": ("docs/overview.md",)})
    readme = next(check for check in result.checks if check.name == "README")

    assert readme.passed is True
    assert readme.message == "docs/overview.md found"
