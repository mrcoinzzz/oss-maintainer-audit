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
