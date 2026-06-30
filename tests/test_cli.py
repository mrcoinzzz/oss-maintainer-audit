from pathlib import Path

from oss_maintainer_audit.cli import main


def test_cli_returns_success_for_healthy_repo(tmp_path: Path, capsys) -> None:
    for filename in (
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "CHANGELOG.md",
        "pyproject.toml",
    ):
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("content\n", encoding="utf-8")

    (tmp_path / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
    (tmp_path / ".github" / "workflows").mkdir(parents=True)

    exit_code = main([str(tmp_path)])

    assert exit_code == 0
    assert "Score: 10/10" in capsys.readouterr().out


def test_cli_can_output_markdown_report(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    exit_code = main([str(tmp_path), "--format", "markdown"])

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "# OSS Maintainer Audit" in output
    assert "| Status | Check | Detail |" in output
    assert "| PASS | README | README.md found |" in output


def test_cli_respects_custom_min_score(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    exit_code = main([str(tmp_path), "--min-score", "10"])

    assert exit_code == 0
    assert "Required: 10%" in capsys.readouterr().out


def test_cli_can_write_report_to_file(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    output_path = tmp_path / "reports" / "audit.md"

    exit_code = main([str(tmp_path), "--format", "markdown", "--output", str(output_path)])

    assert exit_code == 1
    assert capsys.readouterr().out == ""
    output = output_path.read_text(encoding="utf-8")
    assert "# OSS Maintainer Audit" in output
    assert "| PASS | README | README.md found |" in output


def test_cli_can_report_failures_only(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    exit_code = main([str(tmp_path), "--failures-only"])

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "PASS  README" not in output
    assert "WARN  License" in output


def test_cli_failures_only_marks_all_passed_for_healthy_repo(tmp_path: Path, capsys) -> None:
    for filename in (
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "CHANGELOG.md",
        "pyproject.toml",
    ):
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("content\n", encoding="utf-8")

    (tmp_path / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
    (tmp_path / ".github" / "workflows").mkdir(parents=True)

    exit_code = main([str(tmp_path), "--failures-only"])

    assert exit_code == 0
    assert "All checks passed." in capsys.readouterr().out


def test_cli_can_write_github_actions_output(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    output_path = tmp_path / "github-output.txt"

    exit_code = main([str(tmp_path), "--github-output", str(output_path), "--failures-only"])

    assert exit_code == 1
    assert "WARN  License" in capsys.readouterr().out
    output = output_path.read_text(encoding="utf-8")
    assert "passed=1" in output
    assert "total=10" in output
    assert "percent=10" in output
    assert "failing_count=9" in output
    assert "failing_checks=License,Contributing guide" in output


def test_cli_uses_config_file(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    (tmp_path / ".oss-maintainer-audit.json").write_text(
        """
        {
          "min_score": 10,
          "disabled_checks": ["License"]
        }
        """,
        encoding="utf-8",
    )

    exit_code = main([str(tmp_path), "--failures-only"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Required: 10%" in output
    assert "WARN  License" not in output
